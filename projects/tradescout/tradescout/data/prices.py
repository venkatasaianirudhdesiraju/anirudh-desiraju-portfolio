"""Daily OHLCV with on-disk caching. Primary source: Yahoo via yfinance. Fallback: Stooq CSV."""
from __future__ import annotations

import io
import time
from datetime import datetime, timedelta

import httpx
import pandas as pd

from ..config import CACHE, HTTP_UA

COLS = ["open", "high", "low", "close", "volume"]


def _cache_path(ticker: str):
    return CACHE / f"px_{ticker.replace('/', '_')}.csv"


def _from_yfinance(tickers: list[str], start: str) -> dict[str, pd.DataFrame]:
    import yfinance as yf  # optional dependency
    raw = yf.download(tickers, start=start, auto_adjust=True, group_by="ticker", progress=False, threads=True)
    out = {}
    for t in tickers:
        try:
            df = raw[t] if len(tickers) > 1 else raw
        except KeyError:
            continue
        df = df.rename(columns=str.lower)[COLS].dropna()
        if len(df):
            df.index = pd.to_datetime(df.index).tz_localize(None)
            out[t] = df
    return out


def _from_stooq(ticker: str) -> pd.DataFrame | None:
    sym = ticker.lower().replace(".", "-") + ".us"
    try:
        r = httpx.get(f"https://stooq.com/q/d/l/?s={sym}&i=d", headers={"User-Agent": HTTP_UA}, timeout=20)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text), parse_dates=["Date"], index_col="Date").rename(columns=str.lower)
        return df[COLS].dropna() if set(COLS) <= set(df.columns) else None
    except (httpx.HTTPError, ValueError, KeyError):
        return None


def load_prices(tickers: list[str], years: int = 8, refresh_hours: float = 12) -> dict[str, pd.DataFrame]:
    """Returns {ticker: DataFrame[open, high, low, close, volume]} indexed by date."""
    start = (datetime.now() - timedelta(days=365 * years)).strftime("%Y-%m-%d")
    out, stale = {}, []
    for t in tickers:
        p = _cache_path(t)
        if p.exists() and time.time() - p.stat().st_mtime < refresh_hours * 3600:
            out[t] = pd.read_csv(p, index_col=0, parse_dates=True)
        else:
            stale.append(t)
    if stale:
        fetched: dict[str, pd.DataFrame] = {}
        try:
            for i in range(0, len(stale), 50):
                fetched.update(_from_yfinance(stale[i:i + 50], start))
        except Exception as e:  # yfinance missing or blocked → fallback
            print(f"[prices] yfinance unavailable ({type(e).__name__}); trying Stooq")
        for t in stale:
            df = fetched.get(t)
            if df is None or df.empty:
                df = _from_stooq(t)
            if df is not None and len(df) > 60:
                df = df[df.index >= start]
                df.to_csv(_cache_path(t))
                out[t] = df
            elif _cache_path(t).exists():  # keep stale cache rather than nothing
                out[t] = pd.read_csv(_cache_path(t), index_col=0, parse_dates=True)
    return out
