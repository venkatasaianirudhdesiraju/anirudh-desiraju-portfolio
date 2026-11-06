"""python -m hub   → http://localhost:8000

Mounts every project as a sub-app on one server:
  /lifeos/   LifeOS dashboard          /jobfit/    JobFit
  /loglens/  LogLens API (UI: /ui/loglens)   /apisaas/  API starter (docs: /apisaas/docs)
  /ui/dataguard  DataGuard UI           /ui/tradescout  TradeScout reports + run
"""
from __future__ import annotations

import io
import json
import os
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path

PROJECTS = Path(__file__).resolve().parents[2]
for p in ("loglens", "dataguard", "jobfit", "apisaas", "tradescout", "lifeos"):
    sys.path.insert(0, str(PROJECTS / p))
os.environ.setdefault("TRADESCOUT_HOME", str(PROJECTS / "tradescout" / ".tradescout"))
os.environ.setdefault("APISAAS_DB", str(PROJECTS / "apisaas" / "apisaas.db"))

from fastapi import FastAPI, File, Form, HTTPException, UploadFile  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import FileResponse, HTMLResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from . import __version__  # noqa: E402

STATIC = Path(__file__).parent / "static"
app = FastAPI(title="Hub", version=__version__, docs_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
                   allow_methods=["GET"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=STATIC), name="static")

APPS: dict[str, str] = {}


def _mount(prefix: str, module: str, attr: str = "app") -> None:
    """Mount a project; if one fails to import (missing dependency), the rest still work."""
    try:
        mod = __import__(module, fromlist=[attr])
        app.mount(prefix, getattr(mod, attr))
        APPS[prefix] = "ok"
    except Exception as e:  # pragma: no cover - surfaced on the home page
        APPS[prefix] = f"unavailable: {type(e).__name__}: {e}"


def _page(name: str) -> str:
    return (STATIC / name).read_text(encoding="utf-8")


@app.get("/", response_class=HTMLResponse)
def home():
    return _page("index.html")


@app.get("/health")
def health():
    return {"ok": True, "app": "hub", "version": __version__, "apps": APPS}


@app.get("/ui/{name}", response_class=HTMLResponse)
def ui(name: str):
    f = STATIC / f"{name}.html"
    if not f.exists():
        raise HTTPException(404)
    return f.read_text(encoding="utf-8")


# ------------------------------------------------------------------ DataGuard
@app.post("/api/dataguard", response_class=HTMLResponse)
async def dataguard(data: UploadFile = File(...), rules: UploadFile | None = File(None), rules_text: str = Form("")):
    import pandas as pd
    import yaml
    from dataguard.cli import infer_rules
    from dataguard.engine import validate
    from dataguard.report import to_html

    raw = await data.read()
    name = (data.filename or "data.csv").lower()
    if name.endswith(".parquet"):
        df = pd.read_parquet(io.BytesIO(raw))
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(raw))
    elif name.endswith(".json"):
        df = pd.read_json(io.BytesIO(raw))
    else:
        df = pd.read_csv(io.BytesIO(raw))
    text = (await rules.read()).decode() if rules else rules_text
    spec = yaml.safe_load(text) if text.strip() else infer_rules(df)
    return to_html(validate(df, spec, data.filename or "upload"))


# ------------------------------------------------------------------ TradeScout
TS_HOME = Path(os.environ["TRADESCOUT_HOME"])
TS_STATE = {"running": False, "log": "", "started": None, "finished": None}


def _ts_run(args: list[str]) -> None:
    from contextlib import redirect_stderr, redirect_stdout
    from tradescout.cli import main as ts_main
    buf = io.StringIO()
    try:
        with redirect_stdout(buf), redirect_stderr(buf):
            if args[0] == "picks" and not (TS_HOME / "models" / "latest.joblib").exists():
                print("No model yet — training first (a few minutes)…")
                ts_main(["train"] + (["--demo"] if "--demo" in args else []))
            ts_main(args)
    except BaseException:
        buf.write(traceback.format_exc())
    finally:
        TS_STATE.update(running=False, log=buf.getvalue()[-20000:], finished=datetime.now().isoformat(timespec="seconds"))


@app.post("/api/tradescout/run")
def ts_run(cmd: str = Form("picks"), account: float = Form(10000), risk: float = Form(1.0), demo: bool = Form(False)):
    if TS_STATE["running"]:
        raise HTTPException(409, "already running")
    if cmd not in {"picks", "train", "score"}:
        raise HTTPException(422, "cmd must be picks, train or score")
    args = [cmd] + (["--account", str(account), "--risk", str(risk)] if cmd == "picks" else []) + (["--demo"] if demo else [])
    TS_STATE.update(running=True, log="", started=datetime.now().isoformat(timespec="seconds"), finished=None)
    threading.Thread(target=_ts_run, args=(args,), daemon=True).start()
    return {"started": args}


@app.get("/api/tradescout/status")
def ts_status():
    reports = sorted((TS_HOME / "reports").glob("picks_*.html"), reverse=True) if (TS_HOME / "reports").exists() else []
    card = TS_HOME / "models" / "latest.json"
    latest = None
    if reports:
        j = reports[0].with_suffix(".json")
        if j.exists():
            latest = json.loads(j.read_text())
    return {**TS_STATE, "reports": [r.stem for r in reports[:30]],
            "model": json.loads(card.read_text()) if card.exists() else None, "latest": latest}


@app.get("/api/tradescout/report/{stem}")
def ts_report(stem: str):
    f = TS_HOME / "reports" / f"{Path(stem).name}.html"
    if not f.exists():
        raise HTTPException(404)
    return FileResponse(f)


# ------------------------------------------------------------------ mount projects
_mount("/lifeos", "lifeos.app")
_mount("/jobfit", "jobfit.api")
_mount("/loglens", "loglens.api")
_mount("/apisaas", "apisaas.app")
