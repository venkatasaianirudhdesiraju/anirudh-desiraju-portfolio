"""Money logic: card utilization + payoff plan, spending summaries, CSV import with auto-categorization."""
from __future__ import annotations

import csv
import io
import re
from collections import defaultdict

CATEGORY_RULES = [
    ("Groceries", r"walmart|costco|kroger|heb|h-e-b|aldi|trader joe|whole foods|safeway|publix|target|indian grocer|patel"),
    ("Dining", r"restaurant|cafe|coffee|starbucks|mcdonald|chipotle|doordash|uber ?eats|grubhub|pizza|taco|burger|kitchen|grill"),
    ("Transport", r"uber|lyft|shell|exxon|chevron|bp |gas|fuel|parking|toll|metro|airlines|delta|united|southwest"),
    ("Subscriptions", r"netflix|spotify|hulu|disney|youtube|apple\.com|icloud|google \*|openai|anthropic|claude|github|adobe|prime"),
    ("Shopping", r"amazon|amzn|best buy|ebay|etsy|nike|zara|h&m|ikea|apple store"),
    ("Bills & Utilities", r"electric|energy|water|internet|comcast|xfinity|at&t|verizon|t-mobile|insurance|geico|progressive|rent"),
    ("Health & Fitness", r"pharmacy|cvs|walgreens|gym|fitness|planet fitness|doctor|clinic|dental"),
    ("Education", r"udemy|coursera|book|kindle|audible|o'reilly"),
    ("Investing/Transfers", r"robinhood|fidelity|vanguard|schwab|coinbase|zelle|venmo|transfer"),
]
WANTS = {"Dining", "Shopping", "Subscriptions"}


def categorize(merchant: str) -> str:
    m = (merchant or "").lower()
    for cat, pat in CATEGORY_RULES:
        if re.search(pat, m):
            return cat
    return "Other"


def parse_bank_csv(text: str, card: str = "") -> list[dict]:
    """Handles most bank/card exports: finds date / description / amount (or debit+credit) columns by name."""
    rows = list(csv.DictReader(io.StringIO(text.lstrip("﻿"))))
    if not rows:
        return []
    cols = {c.lower().strip(): c for c in rows[0].keys() if c}

    def find(*names):
        for n in names:
            for lc, orig in cols.items():
                if n in lc:
                    return orig
        return None

    c_date = find("transaction date", "posted date", "date")
    c_desc = find("description", "merchant", "payee", "name", "details")
    c_amt, c_debit, c_credit = find("amount"), find("debit"), find("credit")
    c_cat = find("category")
    out = []
    for r in rows:
        try:
            if c_amt:
                amt = float(str(r[c_amt]).replace("$", "").replace(",", "") or 0)
            else:
                amt = -float(str(r.get(c_debit) or 0).replace(",", "") or 0) + float(str(r.get(c_credit) or 0).replace(",", "") or 0)
        except ValueError:
            continue
        # Normalize: purchases are positive spend. Most exports show spend as negative.
        spend = -amt if amt < 0 else amt
        desc = (r.get(c_desc) or "").strip()
        if not desc or re.search(r"payment thank you|autopay|payment received", desc, re.I):
            continue
        cat = categorize(desc)
        if cat == "Other" and c_cat and r.get(c_cat):
            cat = r[c_cat].strip()
        out.append({"date": _iso(r.get(c_date, "")), "merchant": desc[:80], "amount": round(spend, 2), "category": cat,
                    "card": card, "need_or_want": "want" if cat in WANTS else "need"})
    return out


def _iso(d: str) -> str:
    d = (d or "").strip()
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", d)
    if m:
        mo, da, yr = m.groups()
        yr = ("20" + yr) if len(yr) == 2 else yr
        return f"{yr}-{int(mo):02d}-{int(da):02d}"
    return d[:10]


def card_summary(cards: list[dict], extra_payment: float = 0) -> dict:
    total_bal = sum(c.get("balance") or 0 for c in cards)
    total_lim = sum(c.get("limit") or 0 for c in cards)
    util = 100 * total_bal / total_lim if total_lim else 0
    monthly_interest = sum((c.get("balance") or 0) * (c.get("apr") or 0) / 1200 for c in cards)
    # Avalanche: pay minimums on all, throw every extra dollar at the highest APR first (mathematically cheapest).
    order = sorted([c for c in cards if (c.get("balance") or 0) > 0], key=lambda c: -(c.get("apr") or 0))
    months, interest_paid = _simulate_payoff(cards, extra_payment)
    per_card = [{**c, "utilization": round(100 * (c.get("balance") or 0) / c["limit"], 1) if c.get("limit") else None}
                for c in cards]
    advice = []
    if util > 30:
        advice.append(f"Utilization is {util:.0f}%. Getting under 30% (ideally under 10%) helps your credit score.")
    if order:
        advice.append(f"Pay minimums everywhere, then put every extra dollar on {order[0]['name']} ({order[0].get('apr')}% APR) first.")
    if monthly_interest > 0:
        advice.append(f"You're paying about ${monthly_interest:,.0f}/month in interest. That's a guaranteed {max(c.get('apr') or 0 for c in cards):.0f}% return for every dollar paid down.")
    return {"total_balance": round(total_bal, 2), "total_limit": round(total_lim, 2), "utilization": round(util, 1),
            "monthly_interest": round(monthly_interest, 2), "avalanche_order": [c["name"] for c in order],
            "payoff_months": months, "payoff_interest": interest_paid, "cards": per_card, "advice": advice}


def _simulate_payoff(cards: list[dict], extra: float, cap: int = 600) -> tuple[int | None, float]:
    bals = {c["name"]: float(c.get("balance") or 0) for c in cards}
    aprs = {c["name"]: float(c.get("apr") or 0) for c in cards}
    mins = {c["name"]: max(float(c.get("min_payment") or 0), 25.0) for c in cards}
    budget = sum(mins[n] for n in bals if bals[n] > 0) + extra
    paid_interest = 0.0
    for month in range(1, cap + 1):
        for n in bals:
            i = bals[n] * aprs[n] / 1200
            bals[n] += i
            paid_interest += i
        left = budget
        for n in bals:  # minimums
            p = min(mins[n], bals[n], left)
            bals[n] -= p
            left -= p
        for n in sorted(bals, key=lambda n: -aprs[n]):  # avalanche extra
            p = min(bals[n], left)
            bals[n] -= p
            left -= p
        if all(b <= 0.01 for b in bals.values()):
            return month, round(paid_interest, 2)
    return None, round(paid_interest, 2)


def spending_summary(purchases: list[dict], month: str | None = None) -> dict:
    by_month: dict[str, float] = defaultdict(float)
    by_cat: dict[str, float] = defaultdict(float)
    wants = needs = 0.0
    for p in purchases:
        m = (p.get("date") or "")[:7]
        by_month[m] += p.get("amount") or 0
        if month is None or m == month:
            by_cat[p.get("category") or "Other"] += p.get("amount") or 0
            if p.get("need_or_want") == "want":
                wants += p.get("amount") or 0
            else:
                needs += p.get("amount") or 0
    return {"by_month": dict(sorted(by_month.items())),
            "by_category": dict(sorted(by_cat.items(), key=lambda kv: -kv[1])),
            "wants": round(wants, 2), "needs": round(needs, 2)}
