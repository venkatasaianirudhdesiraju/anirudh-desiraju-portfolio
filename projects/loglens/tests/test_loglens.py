from pathlib import Path

from fastapi.testclient import TestClient

from loglens.cli import main
from loglens.core import analyze_texts, to_markdown
from loglens.parser import extract_failures, normalize

SAMPLES = Path(__file__).parent.parent / "sample_logs"


def _texts():
    return {p.name: p.read_text() for p in SAMPLES.glob("*.log")}


def test_normalize_masks_volatile_tokens():
    a = normalize("Timeout at 2026-11-04 02:13:55 from 10.0.0.1:80 id 0xdeadbeef in /var/x/y.py line 42")
    b = normalize("Timeout at 2026-11-05 11:00:01 from 10.9.9.9:81 id 0xBEEF in /opt/z/q.py line 7")
    assert a == b


def test_extracts_pytest_and_generic_blocks():
    fails = extract_failures((SAMPLES / "nightly_run_1.log").read_text())
    assert [f.test for f in fails][:4] == ["test_login_ok", "test_logout_ok", "test_scan_calibration", "test_export_dicom_header"]
    fails2 = extract_failures((SAMPLES / "nightly_run_2.log").read_text())
    assert len(fails2) == 4


def test_fallback_without_markers():
    fails = extract_failures("ok\nValueError: bad thing\nok\n")
    assert len(fails) == 1 and "ValueError" in fails[0].headline


def test_clusters_group_same_root_cause():
    report = analyze_texts(_texts())
    assert report["total_failures"] == 8
    top = report["clusters"][0]
    assert top["count"] == 3 and "ConnectionError" in top["headline"]
    heads = [c["headline"] for c in report["clusters"]]
    assert sum("KeyError" in h for h in heads) == 1      # both PatientID errors merged
    assert sum("AssertionError" in h for h in heads) == 1  # both calibration drifts merged
    assert report["unique_root_causes"] == 4


def test_known_issue_matching():
    report = analyze_texts(_texts(), known_issues=SAMPLES / "known_issues.json")
    assert report["clusters"][0]["known_issue"]["ticket"] == "INFRA-482"
    assert report["known"] == 1
    assert "INFRA-482" in to_markdown(report)


def test_cli_fail_on_new(tmp_path, capsys):
    md = tmp_path / "r.md"
    code = main(["analyze", str(SAMPLES), "--known", str(SAMPLES / "known_issues.json"), "--md", str(md), "--fail-on-new"])
    assert code == 1 and md.read_text().startswith("# LogLens")


def test_cli_learn(tmp_path):
    kb = tmp_path / "kb.json"
    assert main(["learn", "--known", str(kb), "--signature", "KeyError: <STR>", "--ticket", "BUG-1"]) == 0
    assert "BUG-1" in kb.read_text()


def test_api():
    from loglens.api import app
    c = TestClient(app)
    assert c.get("/health").json()["status"] == "ok"
    r = c.post("/analyze", json={"logs": _texts()})
    assert r.status_code == 200 and r.json()["unique_root_causes"] == 4
    files = [("files", (n, t.encode(), "text/plain")) for n, t in _texts().items()]
    r = c.post("/analyze/files?fmt=markdown", files=files)
    assert r.status_code == 200 and "LogLens failure report" in r.text
