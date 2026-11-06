"""Position sizing: fixed-fractional risk with ATR stops, capped by fractional Kelly and a max position size."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Sizing:
    shares: int
    dollars: float
    pct_of_account: float
    stop: float
    target: float
    risk_dollars: float
    kelly_pct: float
    reason: str


def size_position(
    account: float, price: float, atr: float, p_win: float, side: str,
    risk_pct: float = 1.0, stop_atr: float = 1.5, reward_risk: float = 2.0,
    max_pos_pct: float = 10.0, kelly_fraction: float = 0.25,
) -> Sizing:
    """p_win = calibrated probability the trade direction is right.

    1) Risk-based: risk `risk_pct`% of the account between entry and an ATR stop.
    2) Kelly cap: f* = p - (1-p)/b with b = reward/risk; use only `kelly_fraction` of it (quarter Kelly).
    3) Hard cap: never more than `max_pos_pct`% of the account in one name.
    """
    stop_dist = max(stop_atr * atr, price * 0.005)
    sign = 1 if side == "LONG" else -1
    stop = price - sign * stop_dist
    target = price + sign * stop_dist * reward_risk

    b = reward_risk
    kelly = max(0.0, p_win - (1 - p_win) / b)
    kelly_pct = 100 * kelly * kelly_fraction
    if kelly_pct <= 0:
        return Sizing(0, 0, 0, round(stop, 2), round(target, 2), 0, 0, "Kelly ≤ 0: odds don't justify a position")

    risk_dollars = account * risk_pct / 100
    shares_risk = risk_dollars / stop_dist
    # Kelly gives the fraction of capital to put at risk; at-risk dollars / stop distance = shares.
    shares_kelly = account * kelly_pct / 100 / stop_dist
    shares_cap = account * max_pos_pct / 100 / price
    limits = [(shares_risk, "risk budget"), (shares_cap, "max position cap"), (shares_kelly, "fractional Kelly")]
    best, binding = min(limits)
    shares = int(best)
    dollars = shares * price
    return Sizing(shares, round(dollars, 2), round(100 * dollars / account, 2), round(stop, 2), round(target, 2),
                  round(shares * stop_dist, 2), round(kelly_pct, 2), f"limited by {binding}")
