import os
import tempfile

os.environ["LIFEOS_DB"] = os.path.join(tempfile.mkdtemp(), "l.db")
os.environ["TRADESCOUT_HOME"] = tempfile.mkdtemp()
os.environ["APISAAS_DB"] = os.path.join(tempfile.mkdtemp(), "a.db")

import time
from pathlib import Path

from fastapi.testclient import TestClient

from hub.app import APPS, app

c = TestClient(app)
ROOT = Path(__file__).resolve().parents[2]


def test_all_apps_mounted():
    assert all(v == "ok" for v in APPS.values()), APPS
    assert c.get("/health").json()["ok"]
    for path in ["/", "/ui/loglens", "/ui/dataguard", "/ui/tradescout", "/lifeos/", "/jobfit/", "/static/style.css",
                 "/lifeos/static/style.css", "/apisaas/health", "/loglens/health", "/lifeos/api/today"]:
        assert c.get(path).status_code == 200, path


def test_dataguard_route():
    ex = ROOT / "dataguard" / "examples"
    r = c.post("/api/dataguard", files={"data": ("ct.csv", (ex / "ct_scans.csv").read_bytes()),
                                         "rules": ("r.yaml", (ex / "ct_rules.yaml").read_bytes())})
    assert r.status_code == 200 and "FAILED" in r.text
    r = c.post("/api/dataguard", files={"data": ("ct.csv", (ex / "ct_scans.csv").read_bytes())})
    assert "DataGuard report" in r.text  # inferred rules


def test_loglens_and_jobfit_via_hub():
    logs = ROOT / "loglens" / "sample_logs"
    files = [("files", (p.name, p.read_bytes())) for p in logs.glob("*.log")]
    assert c.post("/loglens/analyze/files", files=files).json()["unique_root_causes"] == 4
    ex = ROOT / "jobfit" / "examples"
    r = c.post("/jobfit/fit", json={"resume": (ex / "resume.md").read_text(), "job_description": (ex / "jd_backend.txt").read_text()})
    assert r.json()["score"] > 50


def test_tradescout_demo_run():
    assert c.post("/api/tradescout/run", data={"cmd": "picks", "account": 5000, "demo": "true"}).status_code == 200
    for _ in range(120):
        s = c.get("/api/tradescout/status").json()
        if not s["running"]:
            break
        time.sleep(1)
    assert s["latest"] and len(s["latest"]["picks"]) == 10, s["log"][-2000:]
    assert c.get(f"/api/tradescout/report/{s['reports'][0]}").status_code == 200
