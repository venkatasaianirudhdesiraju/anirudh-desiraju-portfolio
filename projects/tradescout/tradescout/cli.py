"""
python -m tradescout train   [--years 8] [--horizon 1]           # download history, train from scratch, validate
python -m tradescout picks   --account 10000 [--risk 1] [--top 10] # today's top ideas + report (logs to paper ledger)
python -m tradescout score                                        # resolve past paper picks, show live track record
python -m tradescout news    AAPL NVDA                            # see what the news collectors found
Add --demo to train/picks to run fully offline on a synthetic market.
"""
from __future__ import annotations

import argparse
import json
import webbrowser
from pathlib import Path

from . import config, ledger
from . import model as mdl
from .features import build_panel
from .picks import generate
from .report import to_html, to_markdown


def _universe(path: str | None) -> list[str]:
    if path:
        return [t.strip().upper() for t in Path(path).read_text().split() if t.strip()]
    return list(config.DEFAULT_UNIVERSE)


def _prices(args):
    if args.demo:
        from .synthetic import make_market
        return make_market()
    from .data.prices import load_prices
    tickers = sorted(set(_universe(args.universe)) | {config.BENCHMARK})
    print(f"Loading daily prices for {len(tickers)} tickers…")
    return load_prices(tickers, years=getattr(args, "years", 8))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="tradescout", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("train", "picks", "score", "news"):
        s = sub.add_parser(name)
        s.add_argument("--universe", help="file with tickers (default: built-in ~120 liquid names)")
        s.add_argument("--demo", action="store_true", help="offline synthetic market")
        if name == "train":
            s.add_argument("--years", type=int, default=8)
            s.add_argument("--horizon", type=int, default=1, help="days to hold (1 = next day)")
            s.add_argument("--folds", type=int, default=5)
        if name == "picks":
            s.add_argument("--account", type=float, required=True, help="account size in $")
            s.add_argument("--risk", type=float, default=1.0, help="%% of account risked per trade (default 1)")
            s.add_argument("--max-pos", type=float, default=10.0, help="max %% of account per position")
            s.add_argument("--top", type=int, default=10)
            s.add_argument("--no-news", action="store_true")
            s.add_argument("--open", action="store_true", help="open the HTML report")
        if name == "news":
            s.add_argument("tickers", nargs="*")
    a = ap.parse_args(argv)

    if a.cmd == "news":
        from .data.news import collect
        from .sentiment import aggregate
        items = collect([t.upper() for t in a.tickers] or _universe(a.universe)[:20])
        print(json.dumps(aggregate(items), indent=2, default=str))
        return 0

    prices = _prices(a)
    if not prices:
        print("No price data — check your internet connection (or use --demo).")
        return 2

    if a.cmd == "train":
        panel = build_panel(prices, horizon=a.horizon)
        print(f"Training on {len(panel):,} rows · {panel.index.get_level_values('ticker').nunique()} tickers…")
        card = mdl.train(panel, horizon=a.horizon, folds=a.folds)
        print(json.dumps({k: v for k, v in card.__dict__.items() if k != "features"}, indent=2))
        print("\n" + card.verdict)
        return 0

    if a.cmd == "score":
        n = ledger.score_open(prices)
        print(f"Resolved {n} picks.\n" + json.dumps(ledger.stats(), indent=2))
        return 0

    sentiment = {}
    if not a.no_news and not a.demo:
        from .data.news import collect
        from .sentiment import aggregate
        print("Collecting news, filings and Reddit chatter…")
        sentiment = aggregate(collect(list(prices)))
        print(f"  sentiment for {len(sentiment)} tickers")
    res = generate(prices, sentiment, a.account, a.top, a.risk, a.max_pos)
    md, page = to_markdown(res), to_html(res)
    out = config.REPORTS / f"picks_{res['date']}"
    out.with_suffix(".md").write_text(md, encoding="utf-8")
    out.with_suffix(".html").write_text(page, encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    ledger.log_picks(res["picks"])
    print(md)
    print(f"Saved {out}.html / .md / .json · logged {len(res['picks'])} paper picks")
    if a.open:
        webbrowser.open(out.with_suffix(".html").resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
