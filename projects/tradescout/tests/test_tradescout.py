import os
import tempfile

os.environ.setdefault("TRADESCOUT_HOME", tempfile.mkdtemp())

from datetime import datetime, timezone

import pandas as pd
import pytest

from tradescout import ledger
from tradescout import model as mdl
from tradescout.cli import main
from tradescout.data.news import Item, parse_feed
from tradescout.features import FEATURES, build_panel
from tradescout.picks import generate
from tradescout.sentiment import aggregate, lexicon_score
from tradescout.sizing import size_position
from tradescout.synthetic import make_market


@pytest.fixture(scope="module")
def market():
    return make_market(n_tickers=25, days=1200, seed=1, edge=0.15)


def test_features_no_lookahead(market):
    panel = build_panel(market)
    assert set(FEATURES) <= set(panel.columns)
    # Changing tomorrow's price must not change today's features.
    t = "T001"
    m2 = {k: v.copy() for k, v in market.items()}
    m2[t].iloc[-1, :4] *= 1.5
    p2 = build_panel(m2)
    d = panel.xs(t, level="ticker").index[-2]
    a, b = panel.loc[(d, t), FEATURES[:20]], p2.loc[(d, t), FEATURES[:20]]
    pd.testing.assert_series_equal(a, b)


def test_model_finds_real_edge(market):
    card = mdl.train(build_panel(market), folds=3, name="t_edge")
    assert card.oof_auc > 0.55 and card.has_edge, card.verdict


def test_model_admits_no_edge_on_noise():
    noise = make_market(n_tickers=25, days=1200, seed=2, edge=0.0)
    card = mdl.train(build_panel(noise), folds=3, name="t_noise")
    assert card.oof_auc < 0.53 and not card.has_edge


def test_sizing_respects_risk_and_caps():
    s = size_position(10_000, 100, atr=2, p_win=0.6, side="LONG", risk_pct=1, max_pos_pct=10)
    assert s.stop == 97 and s.target == 106
    assert s.risk_dollars <= 100 and s.dollars <= 1000
    short = size_position(10_000, 100, atr=2, p_win=0.6, side="SHORT")
    assert short.stop == 103 and short.target == 94
    assert size_position(10_000, 100, 2, p_win=0.3, side="LONG").shares == 0  # negative Kelly → no trade


def test_sentiment():
    assert lexicon_score("Apple beats estimates, raises guidance, shares surge") > 0.5
    assert lexicon_score("Company misses, cuts outlook amid probe") < -0.5
    assert lexicon_score("did not miss estimates") > 0
    now = datetime.now(timezone.utc)
    agg = aggregate([Item("AAPL", "yahoo", "Apple beats and raises", "", "u", now),
                     Item("AAPL", "reddit/stocks", "AAPL plunges on lawsuit", "", "u", now)])
    assert agg["AAPL"]["buzz"] == 2 and agg["AAPL"]["sentiment"] > 0  # news outweighs reddit


def test_rss_parse():
    xml = """<rss><channel><item><title>NVDA soars</title><link>http://x</link>
             <pubDate>Wed, 04 Nov 2026 10:00:00 GMT</pubDate><description>&lt;p&gt;Record demand&lt;/p&gt;</description></item></channel></rss>"""
    it = parse_feed(xml, "NVDA", "yahoo")[0]
    assert it.title == "NVDA soars" and it.summary == "Record demand" and it.published.year == 2026


def test_picks_and_ledger(market, tmp_path):
    mdl.train(build_panel(market), folds=3, name="latest")
    res = generate(market, {"T003": {"sentiment": 0.8, "buzz": 4, "headlines": []}}, account=25_000, top=10, min_dollar_vol=0)
    picks = res["picks"]
    assert len(picks) == 10
    assert all(50 <= p["confidence"] <= 99 for p in picks)
    assert picks == sorted(picks, key=lambda p: -p["confidence"])
    assert all(p["side"] in {"LONG", "SHORT"} and p["dollars"] <= 2_500 + 1e-6 for p in picks)

    db = tmp_path / "l.db"
    ledger.log_picks(picks, db)
    future = {}
    for t, df in market.items():  # extend prices so picks can resolve
        nxt = df.iloc[[-1]].copy()
        nxt.index = [df.index[-1] + pd.offsets.BDay(1)]
        future[t] = pd.concat([df, nxt])
    assert ledger.score_open(future, db) == 10
    st = ledger.stats(db)
    assert st["resolved"] == 10 and 0 <= st["win_rate"] <= 1


def test_cli_demo(capsys):
    assert main(["train", "--demo", "--folds", "3"]) == 0
    assert main(["picks", "--demo", "--account", "10000"]) == 0
    out = capsys.readouterr().out
    assert "TradeScout — top 10" in out and "Model health" in out
