"""Group failures that share a root cause and rank the groups by impact."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .parser import Failure


@dataclass
class Cluster:
    id: int
    signature: str
    headline: str
    count: int
    tests: list[str]
    sources: list[str]
    known_issue: dict | None = None
    summary: str | None = None
    examples: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _tfidf(docs: list[str]) -> np.ndarray:
    # Char n-grams cope with identifiers like ConnectionRefusedError / test_login_v2.
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=1)
    return vec.fit_transform(docs)


def cluster_failures(failures: list[Failure], threshold: float = 0.6) -> list[Cluster]:
    """Greedy single-pass clustering on cosine similarity of normalized signatures.

    Deterministic and O(n * clusters), which is plenty for CI-sized logs (thousands of failures).
    """
    if not failures:
        return []
    sigs = [f.signature or f.body[:500] for f in failures]
    matrix = _tfidf(sigs)
    sims = cosine_similarity(matrix)

    leaders: list[int] = []
    members: dict[int, list[int]] = {}
    for i in range(len(failures)):
        best, best_sim = None, threshold
        for lead in leaders:
            if sims[i, lead] >= best_sim:
                best, best_sim = lead, sims[i, lead]
        if best is None:
            leaders.append(i)
            members[i] = [i]
        else:
            members[best].append(i)

    clusters = []
    for lead, idxs in members.items():
        fs = [failures[i] for i in idxs]
        clusters.append(
            Cluster(
                id=0,
                signature=sigs[lead],
                headline=failures[lead].headline,
                count=len(fs),
                tests=sorted({f.test for f in fs}),
                sources=sorted({f.source for f in fs}),
                examples=[f.body[:1500] for f in fs[:2]],
            )
        )
    clusters.sort(key=lambda c: (-c.count, c.headline))
    for n, c in enumerate(clusters, 1):
        c.id = n
    return clusters


class KnownIssues:
    """A tiny JSON knowledge base: signatures you've triaged before → ticket + fix notes."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else None
        self.items: list[dict] = []
        if self.path and self.path.exists():
            self.items = json.loads(self.path.read_text(encoding="utf-8"))

    def match(self, clusters: list[Cluster], threshold: float = 0.5) -> None:
        if not self.items or not clusters:
            return
        kb_sigs = [i["signature"] for i in self.items]
        matrix = _tfidf(kb_sigs + [c.signature for c in clusters])
        sims = cosine_similarity(matrix[len(kb_sigs):], matrix[: len(kb_sigs)])
        for c, row in zip(clusters, sims):
            j = int(row.argmax())
            if row[j] >= threshold:
                c.known_issue = {**self.items[j], "similarity": round(float(row[j]), 3)}

    def add(self, signature: str, ticket: str, notes: str = "") -> None:
        self.items.append({"signature": signature, "ticket": ticket, "notes": notes})
        if self.path:
            self.path.write_text(json.dumps(self.items, indent=2), encoding="utf-8")
