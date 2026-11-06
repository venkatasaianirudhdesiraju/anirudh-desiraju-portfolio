"""Synthetic market with a small, real, learnable signal — for tests and `--demo` runs without internet."""
from __future__ import annotations

import numpy as np
import pandas as pd


def make_market(n_tickers: int = 30, days: int = 1500, seed: int = 0, edge: float = 0.15) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=days)
    mkt = rng.normal(0.0003, 0.01, days)
    out = {}
    for i in range(n_tickers + 1):
        name = "SPY" if i == 0 else f"T{i:03d}"
        r = np.zeros(days)
        beta = 1.0 if i == 0 else rng.uniform(0.6, 1.4)
        noise = rng.normal(0, 0.015 if i else 0.0, days)
        for t in range(days):
            # planted short-term mean reversion: yesterday's 5d move partly reverses
            mr = -edge * r[max(t - 5, 0):t].sum() if t > 5 and i else 0.0
            r[t] = beta * mkt[t] + noise[t] + mr
        close = 50 * np.exp(np.cumsum(r)) * (1 + i / 10)
        hi = close * (1 + np.abs(rng.normal(0, 0.008, days)))
        lo = close * (1 - np.abs(rng.normal(0, 0.008, days)))
        op = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.003, days))
        vol = rng.lognormal(15, 0.3, days)
        out[name] = pd.DataFrame({"open": op, "high": np.maximum.reduce([hi, op, close]),
                                  "low": np.minimum.reduce([lo, op, close]), "close": close, "volume": vol}, index=idx)
    return out
