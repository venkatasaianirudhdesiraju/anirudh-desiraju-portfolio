"""Daily pipeline: prices → features → model probability → news sentiment tilt → top-N sized trade ideas."""
from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd

from . import model as mdl
from .features import build_panel
from .sizing import size_position

SENTIMENT_TILT = 0.03  # max ±3 percentage points added to P(up) from news. Heuristic — NOT validated by backtest.


def generate(
    prices: dict[str, pd.DataFrame], sentiment: dict[str, dict], account: float, top: int = 10,
    risk_pct: float = 1.0, max_pos_pct: float = 10.0, min_dollar_vol: float = 2e7, model_name: str = "latest",
) -> dict:
    bundle = mdl.load(model_name)
    card = bundle["card"]
    panel = build_panel(prices, horizon=card["horizon"])
    last_date = panel.index.get_level_values("date").max()
    today = panel.xs(last_date, level="date").copy()

    # Liquidity filter: skip names you couldn't trade size in without slippage.
    dv = {t: float((df["close"] * df["volume"]).tail(20).mean()) for t, df in prices.items()}
    today = today[[dv.get(t, 0) >= min_dollar_vol and today.loc[t, "close"] >= 5 for t in today.index]]
    if today.empty:
        return {"date": str(last_date.date()), "picks": [], "model": card}

    p = mdl.predict(bundle, today)
    sent = np.array([sentiment.get(t, {}).get("sentiment", 0.0) for t in today.index])
    p_adj = np.clip(p + SENTIMENT_TILT * sent, 0.01, 0.99)
    today["model_p"], today["p_up"], today["sent"] = p, p_adj, sent
    today["side"] = np.where(p_adj >= 0.5, "LONG", "SHORT")
    today["confidence"] = np.maximum(p_adj, 1 - p_adj)
    best = today.sort_values("confidence", ascending=False).head(top)

    picks = []
    for t, row in best.iterrows():
        sz = size_position(account, row.close, row.atr, row.confidence, row.side, risk_pct=risk_pct, max_pos_pct=max_pos_pct)
        s = sentiment.get(t, {})
        picks.append({
            "date": str(last_date.date()), "ticker": t, "side": row.side, "confidence": round(100 * row.confidence, 1),
            "model_p": round(float(row.model_p), 4), "sentiment": round(float(row.sent), 3), "buzz": s.get("buzz", 0),
            "price": round(float(row.close), 2), "stop": sz.stop, "target": sz.target, "shares": sz.shares,
            "dollars": sz.dollars, "pct_of_account": sz.pct_of_account, "risk_dollars": sz.risk_dollars,
            "kelly_pct": sz.kelly_pct, "sizing_note": sz.reason, "horizon": card["horizon"],
            "why": _why(row), "headlines": s.get("headlines", []),
        })
    return {"date": str(last_date.date()), "generated": datetime.now().isoformat(timespec="minutes"),
            "account": account, "picks": picks, "model": card}


def _why(r: pd.Series) -> str:
    bits = []
    if abs(r.ret_5) > 0.03:
        bits.append(f"{'up' if r.ret_5 > 0 else 'down'} {abs(r.ret_5):.1%} in 5d")
    if r.rsi_14 > 70 or r.rsi_14 < 30:
        bits.append(f"RSI {r.rsi_14:.0f} ({'overbought' if r.rsi_14 > 70 else 'oversold'})")
    if abs(r.dist_sma50) > 0.05:
        bits.append(f"{r.dist_sma50:+.1%} vs 50-day avg")
    if r.volume_z > 1.5:
        bits.append("unusual volume")
    if abs(r.sent) > 0.2:
        bits.append(f"news {'positive' if r.sent > 0 else 'negative'} ({r.sent:+.2f})")
    return "; ".join(bits) or "model pattern (no single dominant factor)"
