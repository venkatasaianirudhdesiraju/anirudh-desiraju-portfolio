"""REST API: uvicorn loglens.api:app --reload"""
from __future__ import annotations

import os

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from . import __version__, llm
from .core import analyze_texts, to_markdown

app = FastAPI(title="LogLens", version=__version__,
              description="Cluster CI test failures into root causes, match known issues, and triage with a local LLM.")
KNOWN = os.getenv("LOGLENS_KNOWN_ISSUES")
MAX_BYTES = 20 * 1024 * 1024


class TextIn(BaseModel):
    logs: dict[str, str]
    threshold: float = 0.6
    use_llm: bool = False


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__, "ollama": llm.ollama_available()}


@app.post("/analyze")
def analyze(body: TextIn) -> dict:
    if not body.logs:
        raise HTTPException(422, "logs is empty")
    return analyze_texts(body.logs, body.threshold, KNOWN, body.use_llm)


@app.post("/analyze/files")
async def analyze_files(
    files: list[UploadFile] = File(...),
    threshold: float = Query(0.6, ge=0, le=1),
    use_llm: bool = False,
    fmt: str = Query("json", pattern="^(json|markdown)$"),
):
    texts, total = {}, 0
    for f in files:
        data = await f.read()
        total += len(data)
        if total > MAX_BYTES:
            raise HTTPException(413, "upload too large (20 MB max)")
        texts[f.filename or "upload"] = data.decode("utf-8", errors="replace")
    report = analyze_texts(texts, threshold, KNOWN, use_llm)
    return PlainTextResponse(to_markdown(report)) if fmt == "markdown" else report
