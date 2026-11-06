"""Train a direction model from scratch with walk-forward validation, calibration and an honest edge check."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import roc_auc_score

from .config import MODELS
from .features import FEATURES

COST_BPS = 5  # per side, slippage + fees


def _make_model(seed: int = 0) -> HistGradientBoostingClassifier:
    return HistGradientBoostingClassifier(
        learning_rate=0.04, max_iter=300, max_leaf_nodes=31, min_samples_leaf=200,
        l2_regularization=1.0, early_stopping=True, validation_fraction=0.1, random_state=seed,
    )


@dataclass
class ModelCard:
    trained_at: str
    horizon: int
    n_rows: int
    n_tickers: int
    date_range: list[str]
    oof_auc: float
    oof_accuracy: float
    calibration_table: list[dict]          # confidence bucket → realized hit rate
    backtest: dict
    has_edge: bool
    verdict: str
    features: list[str] = field(default_factory=lambda: list(FEATURES))


def walk_forward_oof(panel: pd.DataFrame, folds: int = 5, embargo: int = 5, min_train_frac: float = 0.4) -> pd.Series:
    """Out-of-fold probabilities: train only on the past, skip `embargo` days, predict the next block."""
    dates = panel.index.get_level_values("date").unique().sort_values()
    start = int(len(dates) * min_train_frac)
    blocks = np.array_split(dates[start:], folds)
    y = (panel["fwd_ret"] > 0).astype(int)
    oof = pd.Series(np.nan, index=panel.index)
    lvl = panel.index.get_level_values("date")
    for i, block in enumerate(blocks):
        if len(block) == 0:
            continue
        train_end = dates[max(dates.get_loc(block[0]) - embargo, 1)]
        tr, te = lvl < train_end, (lvl >= block[0]) & (lvl <= block[-1])
        m = _make_model(i).fit(panel.loc[tr, FEATURES], y[tr])
        oof[te] = m.predict_proba(panel.loc[te, FEATURES])[:, 1]
    return oof


def backtest(panel: pd.DataFrame, prob: pd.Series, k: int = 5, min_conf: float = 0.52) -> dict:
    """Each day: long top-k by P(up), short top-k by P(down), equal weight, only if confidence ≥ min_conf.

    Returns are next-period close→close minus costs. Overlapping horizons are not compounded (horizon=1 assumed
    for the equity curve; longer horizons report mean per-trade return)."""
    df = pd.DataFrame({"p": prob, "r": panel["fwd_ret"]}).dropna()
    cost = 2 * COST_BPS / 1e4
    daily, trades, wins = [], 0, 0
    for d, g in df.groupby(level="date"):
        longs = g[g.p >= min_conf].nlargest(k, "p")
        shorts = g[(1 - g.p) >= min_conf].nsmallest(k, "p")
        rets = list(longs.r - cost) + list(-shorts.r - cost)
        if rets:
            daily.append((d, float(np.mean(rets))))
            trades += len(rets)
            wins += sum(x > 0 for x in rets)
    if not daily:
        return {"days": 0, "trades": 0}
    s = pd.Series(dict(daily)).sort_index()
    eq = (1 + s).cumprod()
    dd = (eq / eq.cummax() - 1).min()
    sharpe = s.mean() / s.std() * np.sqrt(252) if s.std() > 0 else 0.0
    return {
        "days": len(s), "trades": trades, "win_rate": round(wins / trades, 4),
        "avg_trade_ret_pct": round(100 * s.mean(), 4), "total_return_pct": round(100 * (eq.iloc[-1] - 1), 2),
        "sharpe": round(float(sharpe), 2), "max_drawdown_pct": round(100 * float(dd), 2),
        "period": [str(s.index[0].date()), str(s.index[-1].date())],
    }


def calibration_table(prob: pd.Series, y: pd.Series) -> list[dict]:
    conf = np.maximum(prob, 1 - prob)
    correct = ((prob >= 0.5) == (y == 1))
    out = []
    for lo, hi in [(0.5, 0.52), (0.52, 0.55), (0.55, 0.6), (0.6, 0.7), (0.7, 1.01)]:
        m = (conf >= lo) & (conf < hi)
        if m.sum() >= 30:
            out.append({"confidence": f"{int(lo*100)}-{min(int(hi*100),100)}%", "n": int(m.sum()),
                        "hit_rate": round(float(correct[m].mean()), 4)})
    return out


def train(panel: pd.DataFrame, horizon: int = 1, folds: int = 5, name: str = "latest") -> ModelCard:
    data = panel.dropna(subset=["fwd_ret"])
    y = (data["fwd_ret"] > 0).astype(int)
    oof = walk_forward_oof(data, folds=folds, embargo=max(5, horizon))
    m = oof.notna()
    auc = float(roc_auc_score(y[m], oof[m]))

    # Calibrate on out-of-fold predictions, so "65%" means it was right ~65% of the time out of sample.
    iso = IsotonicRegression(out_of_bounds="clip", y_min=0.01, y_max=0.99).fit(oof[m], y[m])
    cal = pd.Series(iso.predict(oof[m]), index=oof[m].index)
    acc = float(((cal >= 0.5) == (y[m] == 1)).mean())
    bt = backtest(data[m], cal)
    base = float(y[m].mean())

    has_edge = bool(auc >= 0.52 and bt.get("sharpe", 0) > 0.5 and bt.get("avg_trade_ret_pct", 0) > 0)
    verdict = (
        f"Out-of-sample AUC {auc:.3f} (0.5 = coin flip), accuracy {acc:.1%} vs {max(base, 1-base):.1%} by always "
        f"guessing the majority, backtest Sharpe {bt.get('sharpe', 0)} after costs. "
        + ("Some edge detected — still paper trade before using real money."
           if has_edge else "NO reliable edge detected — treat picks as a watchlist, not trade signals.")
    )

    final = _make_model(99).fit(data[FEATURES], y)
    dates = data.index.get_level_values("date")
    card = ModelCard(
        trained_at=datetime.now().isoformat(timespec="seconds"), horizon=horizon, n_rows=len(data),
        n_tickers=data.index.get_level_values("ticker").nunique(), date_range=[str(dates.min().date()), str(dates.max().date())],
        oof_auc=round(auc, 4), oof_accuracy=round(acc, 4), calibration_table=calibration_table(cal, y[m]),
        backtest=bt, has_edge=has_edge, verdict=verdict,
    )
    joblib.dump({"model": final, "calibrator": iso, "card": asdict(card)}, MODELS / f"{name}.joblib")
    (MODELS / f"{name}.json").write_text(json.dumps(asdict(card), indent=2))
    return card


def load(name: str = "latest") -> dict:
    path = MODELS / f"{name}.joblib"
    if not path.exists():
        raise FileNotFoundError("No trained model yet — run: python -m tradescout train")
    return joblib.load(path)


def predict(bundle: dict, rows: pd.DataFrame) -> np.ndarray:
    raw = bundle["model"].predict_proba(rows[FEATURES])[:, 1]
    return bundle["calibrator"].predict(raw)
