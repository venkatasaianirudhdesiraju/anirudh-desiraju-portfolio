"""Optional local-LLM summaries via Ollama. Everything works without it."""
from __future__ import annotations

import os

import httpx

from .cluster import Cluster

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

PROMPT = """You are a senior test engineer triaging CI failures.
{count} test(s) failed with the same signature. Tests: {tests}

Representative failure output:
{example}

In 3 short bullet points: (1) the most likely root cause, (2) whether this looks like a product bug,
test bug, or environment/infra issue, (3) the first thing to check. Be concrete and brief."""


def ollama_available(timeout: float = 1.5) -> bool:
    try:
        return httpx.get(f"{OLLAMA_URL}/api/tags", timeout=timeout).status_code == 200
    except httpx.HTTPError:
        return False


def summarize(cluster: Cluster, timeout: float = 120.0) -> str | None:
    prompt = PROMPT.format(
        count=cluster.count,
        tests=", ".join(cluster.tests[:10]),
        example=(cluster.examples[0] if cluster.examples else cluster.signature)[:3000],
    )
    try:
        r = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.2}},
            timeout=timeout,
        )
        r.raise_for_status()
        return r.json().get("response", "").strip() or None
    except httpx.HTTPError:
        return None
