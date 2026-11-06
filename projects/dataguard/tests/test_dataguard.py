from pathlib import Path

import pandas as pd

from dataguard import load_rules, validate
from dataguard.cli import infer_rules, main
from dataguard.report import to_html

EX = Path(__file__).parent.parent / "examples"


def _report():
    return validate(pd.read_csv(EX / "ct_scans.csv"), load_rules(EX / "ct_rules.yaml"), "ct_scans.csv")


def test_finds_every_planted_defect():
    r = _report()
    bad = {(x.column, x.check) for x in r.errors + r.warnings}
    assert ("patient_id", "regex") in bad
    assert ("kvp", "max") in bad
    assert ("dose_mgy", "outlier_z") in bad
    assert ("status", "allowed") in bad
    assert ("scanned_at", "not_future") in bad
    assert ("scan_id", "unique") in bad
    assert not r.passed and 0 < r.score < 100


def test_clean_data_passes():
    df = pd.read_csv(EX / "ct_scans.csv").drop([3, 10, 20, 30, 40, 50])
    r = validate(df, load_rules(EX / "ct_rules.yaml"))
    assert r.passed, [(x.column, x.check, x.sample) for x in r.errors + r.warnings]


def test_missing_column_and_types():
    df = pd.DataFrame({"a": ["1", "x", "3"]})
    r = validate(df, {"columns": {"a": {"type": "number"}, "b": {"required": True}}})
    checks = {(x.column, x.check): x for x in r.results}
    assert checks[("a", "type")].failed_rows == 1
    assert not checks[("b", "exists")].passed


def test_html_and_cli(tmp_path):
    assert "DataGuard report" in to_html(_report())
    out = tmp_path / "r.html"
    assert main(["check", str(EX / "ct_scans.csv"), "--rules", str(EX / "ct_rules.yaml"), "--html", str(out)]) == 1
    assert out.exists()


def test_infer_rules_roundtrip():
    df = pd.read_csv(EX / "ct_scans.csv").drop([3, 10, 20, 30, 40, 50])
    rules = infer_rules(df)
    assert rules["columns"]["status"]["allowed"] == ["ok", "rejected", "retake"]
    assert validate(df, rules).passed
