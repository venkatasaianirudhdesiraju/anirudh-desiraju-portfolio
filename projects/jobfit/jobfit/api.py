"""uvicorn jobfit.api:app  → open http://localhost:8000"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import __version__
from .llm import tailor
from .scoring import score

app = FastAPI(title="JobFit", version=__version__)
PAGE = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


class FitIn(BaseModel):
    resume: str = Field(min_length=50)
    job_description: str = Field(min_length=50)
    tailor: bool = False


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return PAGE


@app.post("/fit")
def fit(body: FitIn) -> dict:
    out = score(body.resume, body.job_description).to_dict()
    if body.tailor:
        out["tailored"] = tailor(body.resume, body.job_description) or "Local model unavailable — run `ollama serve`."
    return out
