"""Paper-trading ledger: every pick is logged, then scored against what the market actually did."""
from __future__ import annotations

import sqlite3

import pandas as pd

from .config import LEDGER_DB

SCHEMA = """CREATE TABLE IF NOT EXISTS picks (
  pick_date TEXT, ticker TEXT, side TEXT, confidence REAL, entry REAL, stop REAL, target REAL, shares INTEGER,
  horizon INTEGER, sentiment REAL, buzz INTEGER, model_p REAL,
  exit_date TEXT, exit_price REAL, outcome TEXT, ret_pct REAL, pnl REAL,
  PRIMARY KEY (pick_date, ticker))"""


def _conn(path=LEDGER_DB):
    c = sqlite3.connect(path)
    c.execute(SCHEMA)
    return c


def log_picks(picks: list[dict], path=LEDGER_DB) -> None:
    with _conn(path) as c:
        for p in picks:
            c.execute("""INSERT OR REPLACE INTO picks(pick_date,ticker,side,confidence,entry,stop,target,shares,horizon,
                         sentiment,buzz,model_p) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (p["date"], p["ticker"], p["side"], p["confidence"], p["price"], p["stop"], p["target"],
                       p["shares"], p["horizon"], p["sentiment"], p["buzz"], p["model_p"]))


def score_open(prices: dict[str, pd.DataFrame], path=LEDGER_DB) -> int:
    """Resolve picks whose horizon has passed: stop hit, target hit (checked on daily high/low), or time exit."""
    n = 0
    with _conn(path) as c:
        rows = c.execute("SELECT pick_date,ticker,side,entry,stop,target,shares,horizon FROM picks WHERE outcome IS NULL").fetchall()
        for d, t, side, entry, stop, target, shares, hz in rows:
            df = prices.get(t)
            if df is None:
                continue
            after = df[df.index > pd.Timestamp(d)].head(hz)
            if len(after) < hz:
                continue
            exit_px, exit_d, outcome = after["close"].iloc[-1], after.index[-1], "time"
            for day, bar in after.iterrows():
                hit_stop = bar.low <= stop if side == "LONG" else bar.high >= stop
                hit_tgt = bar.high >= target if side == "LONG" else bar.low <= target
                if hit_stop:  # conservative: if both in one bar, assume the stop hit first
                    exit_px, exit_d, outcome = stop, day, "stop"
                    break
                if hit_tgt:
                    exit_px, exit_d, outcome = target, day, "target"
                    break
            sign = 1 if side == "LONG" else -1
            ret = sign * (exit_px / entry - 1)
            c.execute("UPDATE picks SET exit_date=?,exit_price=?,outcome=?,ret_pct=?,pnl=? WHERE pick_date=? AND ticker=?",
                      (str(exit_d.date()), float(exit_px), outcome, round(100 * ret, 3), round(sign * (exit_px - entry) * shares, 2), d, t))
            n += 1
    return n


def stats(path=LEDGER_DB) -> dict:
    with _conn(path) as c:
        df = pd.read_sql("SELECT * FROM picks", c)
    done = df[df.outcome.notna()]
    if done.empty:
        return {"logged": len(df), "resolved": 0}
    by_conf = done.assign(bucket=pd.cut(done.confidence, [0, 55, 60, 65, 100])).groupby("bucket", observed=True)
    return {
        "logged": len(df), "resolved": len(done), "win_rate": round(float((done.ret_pct > 0).mean()), 4),
        "avg_ret_pct": round(float(done.ret_pct.mean()), 3), "total_pnl": round(float(done.pnl.sum()), 2),
        "by_confidence": {str(k): {"n": len(g), "win_rate": round(float((g.ret_pct > 0).mean()), 3)} for k, g in by_conf},
    }
