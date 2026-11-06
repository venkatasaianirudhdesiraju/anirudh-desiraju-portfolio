"""Optional: rewrite resume bullets toward a JD using a local Ollama model. Never invents experience."""
from __future__ import annotations

import os

import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

PROMPT = """You are an expert technical resume writer. Rewrite the candidate's resume bullets so they match the job
description's language and priorities. RULES: only use facts present in the resume — never invent tools, employers,
numbers or experience. Keep each bullet under 30 words, start with a strong verb, keep any metrics.
Output 6-8 bullets, then a 2-sentence tailored summary, then one line listing skills the candidate truly lacks.

JOB DESCRIPTION:
{jd}

RESUME:
{resume}"""


def tailor(resume: str, jd: str, timeout: float = 180) -> str | None:
    try:
        r = httpx.post(f"{OLLAMA_URL}/api/generate", timeout=timeout, json={
            "model": OLLAMA_MODEL, "prompt": PROMPT.format(jd=jd[:6000], resume=resume[:8000]),
            "stream": False, "options": {"temperature": 0.3}})
        r.raise_for_status()
        return r.json().get("response", "").strip() or None
    except httpx.HTTPError:
        return None
