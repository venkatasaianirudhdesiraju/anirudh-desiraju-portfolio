"""Technical + cross-sectional features from daily OHLCV. All features at date t use data up to t only."""
from __future__ import annotations

import numpy as np
import pandas as pd

FEATURES = [
    "ret_1", "ret_5", "ret_10", "ret_20", "ret_60", "vol_10", "vol_20", "vol_ratio", "rsi_14", "macd_hist",
    "dist_sma20", "dist_sma50", "dist_sma200", "dist_high_252", "dist_low_252", "atr_pct", "gap",
    "volume_z", "range_pos", "rs_spy_5", "rs_spy_20", "spy_ret_5", "spy_vol_20", "dow",
    "xs_rank_ret_5", "xs_rank_ret_20", "xs_rank_vol_20",
]


def _rsi(close: pd.Series, n: int = 14) -> pd.Series:
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def ticker_features(df: pd.DataFrame, spy: pd.DataFrame | None) -> pd.DataFrame:
    c, h, l, o, v = df["close"], df["high"], df["low"], df["open"], df["volume"]
    r = c.pct_change()
    f = pd.DataFrame(index=df.index)
    for n in (1, 5, 10, 20, 60):
        f[f"ret_{n}"] = c.pct_change(n)
    f["vol_10"] = r.rolling(10).std()
    f["vol_20"] = r.rolling(20).std()
    f["vol_ratio"] = f["vol_10"] / f["vol_20"]
    f["rsi_14"] = _rsi(c)
    ema12, ema26 = c.ewm(span=12).mean(), c.ewm(span=26).mean()
    macd = ema12 - ema26
    f["macd_hist"] = (macd - macd.ewm(span=9).mean()) / c
    for n in (20, 50, 200):
        f[f"dist_sma{n}"] = c / c.rolling(n).mean() - 1
    f["dist_high_252"] = c / c.rolling(252, min_periods=60).max() - 1
    f["dist_low_252"] = c / c.rolling(252, min_periods=60).min() - 1
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    f["atr"] = tr.rolling(14).mean()
    f["atr_pct"] = f["atr"] / c
    f["gap"] = o / c.shift() - 1
    lv = np.log1p(v)
    f["volume_z"] = (lv - lv.rolling(20).mean()) / lv.rolling(20).std()
    f["range_pos"] = (c - l) / (h - l).replace(0, np.nan)
    if spy is not None:
        sc = spy["close"].reindex(df.index).ffill()
        f["spy_ret_5"] = sc.pct_change(5)
        f["spy_vol_20"] = sc.pct_change().rolling(20).std()
        f["rs_spy_5"] = f["ret_5"] - f["spy_ret_5"]
        f["rs_spy_20"] = f["ret_20"] - sc.pct_change(20)
    else:
        f["spy_ret_5"] = f["spy_vol_20"] = f["rs_spy_5"] = f["rs_spy_20"] = 0.0
    f["dow"] = df.index.dayofweek
    f["close"] = c
    return f


def build_panel(prices: dict[str, pd.DataFrame], horizon: int = 1, benchmark: str = "SPY") -> pd.DataFrame:
    """Long panel indexed by (date, ticker). Target = forward `horizon`-day return (close→close)."""
    spy = prices.get(benchmark)
    frames = []
    for t, df in prices.items():
        if len(df) < 260:
            continue
        f = ticker_features(df, spy)
        f["fwd_ret"] = df["close"].shift(-horizon) / df["close"] - 1
        f["ticker"] = t
        frames.append(f)
    panel = pd.concat(frames).reset_index().rename(columns={"index": "date", "Date": "date"})
    panel = panel.set_index(["date", "ticker"]).sort_index()
    # Cross-sectional ranks (0..1) per day — what matters for picking the best names *today*.
    g = panel.groupby(level="date")
    panel["xs_rank_ret_5"] = g["ret_5"].rank(pct=True)
    panel["xs_rank_ret_20"] = g["ret_20"].rank(pct=True)
    panel["xs_rank_vol_20"] = g["vol_20"].rank(pct=True)
    panel = panel.replace([np.inf, -np.inf], np.nan)
    return panel.dropna(subset=["ret_60", "dist_sma50", "atr_pct", "rsi_14"])
