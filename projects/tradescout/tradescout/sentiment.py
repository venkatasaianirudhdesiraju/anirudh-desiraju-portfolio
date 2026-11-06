"""Financial sentiment scoring.

Default: built-in finance lexicon (Loughran-McDonald style) with negation handling — zero dependencies.
If `transformers` + `torch` are installed and TRADESCOUT_FINBERT=1, uses ProsusAI/finbert instead.
"""
from __future__ import annotations

import math
import os
import re
from collections import defaultdict
from datetime import datetime, timezone

POS = set("""beat beats beating surge surges surged soar soars soared jump jumps jumped rally rallies rallied
gain gains gained record upgrade upgraded upgrades outperform outperforms bullish buy strong stronger strength
growth grow grows grew raise raises raised boost boosts boosted profit profitable profits exceed exceeds exceeded
expand expands expansion approval approved approves win wins won breakthrough partnership acquire acquisition
dividend buyback repurchase optimistic positive upbeat robust tops topped higher high highs rebound rebounds
accelerate accelerates momentum innovative launch launches launched demand overweight""".split())
NEG = set("""miss misses missed plunge plunges plunged sink sinks sank tumble tumbles tumbled drop drops dropped
fall falls fell slump slumps slumped downgrade downgraded downgrades underperform bearish sell weak weaker weakness
loss losses lose losing decline declines declined cut cuts cutting lawsuit sue sued probe investigation fraud
recall recalls warning warns warned layoff layoffs bankruptcy default delay delayed delays halt halted ban banned
fine fined penalty concern concerns risk risks volatile lower low lows slowdown slows slowing disappointing
disappoint disappoints resign resigns resigned subpoena short underweight dilution offering""".split())
NEGATORS = {"not", "no", "never", "without", "fails", "failed", "didn't", "doesn't", "isn't", "wasn't"}
WORD = re.compile(r"[a-z']+")

_finbert = None


def _finbert_score(texts: list[str]) -> list[float]:
    global _finbert
    if _finbert is None:
        from transformers import pipeline
        _finbert = pipeline("text-classification", model="ProsusAI/finbert", truncation=True)
    out = []
    for r in _finbert(texts, batch_size=16):
        out.append({"positive": 1, "negative": -1}.get(r["label"], 0) * r["score"])
    return out


def lexicon_score(text: str) -> float:
    """-1..1"""
    words = WORD.findall(text.lower())
    s = 0.0
    for i, w in enumerate(words):
        v = 1.0 if w in POS else -1.0 if w in NEG else 0.0
        if v and any(x in NEGATORS for x in words[max(0, i - 3):i]):
            v = -v
        s += v
    return math.tanh(s / 3)


def score_texts(texts: list[str]) -> list[float]:
    if os.getenv("TRADESCOUT_FINBERT") == "1":
        try:
            return _finbert_score(texts)
        except Exception as e:  # missing deps / model download blocked
            print(f"[sentiment] FinBERT unavailable ({type(e).__name__}); using lexicon")
    return [lexicon_score(t) for t in texts]


SOURCE_WEIGHT = {"sec": 1.5, "yahoo": 1.0, "google_news": 1.0}  # reddit / blogs default 0.6


def aggregate(items) -> dict[str, dict]:
    """Per-ticker: recency- and source-weighted mean sentiment, buzz (item count), and top headlines."""
    if not items:
        return {}
    scores = score_texts([it.text for it in items])
    now = datetime.now(timezone.utc)
    acc: dict[str, dict] = defaultdict(lambda: {"w": 0.0, "s": 0.0, "n": 0, "heads": []})
    for it, sc in zip(items, scores):
        age_h = (now - it.published).total_seconds() / 3600 if it.published else 24
        w = SOURCE_WEIGHT.get(it.source, 0.6) * math.exp(-max(age_h, 0) / 24)
        a = acc[it.ticker]
        a["w"] += w
        a["s"] += w * sc
        a["n"] += 1
        a["heads"].append((abs(sc) * w, sc, it.title, it.source, it.url))
    out = {}
    for t, a in acc.items():
        heads = sorted(a["heads"], reverse=True)[:3]
        out[t] = {"sentiment": a["s"] / a["w"] if a["w"] else 0.0, "buzz": a["n"],
                  "headlines": [{"score": round(h[1], 2), "title": h[2], "source": h[3], "url": h[4]} for h in heads]}
    return out
