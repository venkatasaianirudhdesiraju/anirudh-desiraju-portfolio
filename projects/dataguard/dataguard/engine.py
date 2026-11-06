"""Rules engine. A rules file (YAML) describes columns and table-level checks:

table:
  min_rows: 1
  unique: [patient_id, scan_id]
columns:
  patient_id: {type: string, required: true, regex: "^P\\d{6}$"}
  kvp:        {type: number, min: 70, max: 140}
  status:     {allowed: [ok, retake, rejected]}
  scanned_at: {type: datetime, not_future: true}
  dose_mgy:   {type: number, max_null_pct: 1, outlier_z: 4}
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

import numpy as np
import warnings

import pandas as pd

warnings.filterwarnings("ignore", message="Could not infer format")
import yaml


@dataclass
class CheckResult:
    check: str
    column: str | None
    passed: bool
    failed_rows: int = 0
    detail: str = ""
    severity: str = "error"  # error | warn
    sample: list[Any] = field(default_factory=list)


@dataclass
class Report:
    source: str
    rows: int
    columns: int
    results: list[CheckResult]
    profile: dict[str, dict]

    @property
    def errors(self) -> list[CheckResult]:
        return [r for r in self.results if not r.passed and r.severity == "error"]

    @property
    def warnings(self) -> list[CheckResult]:
        return [r for r in self.results if not r.passed and r.severity == "warn"]

    @property
    def passed(self) -> bool:
        return not self.errors

    @property
    def score(self) -> float:
        return round(100 * sum(r.passed for r in self.results) / max(len(self.results), 1), 1)

    def to_dict(self) -> dict:
        d = asdict(self)
        d.update(passed=self.passed, score=self.score)
        return d


def load_rules(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def load_table(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    suf = p.suffix.lower()
    if suf == ".parquet":
        return pd.read_parquet(p)
    if suf in {".xlsx", ".xls"}:
        return pd.read_excel(p)
    if suf == ".json":
        return pd.read_json(p)
    return pd.read_csv(p)


def _sample(series: pd.Series, n: int = 5) -> list:
    return [None if pd.isna(v) else (v.item() if hasattr(v, "item") else str(v)) for v in series.head(n)]


def _result(name, col, bad: pd.Series, detail="", severity="error") -> CheckResult:
    """bad: the offending values (already filtered)."""
    return CheckResult(name, col, bad.empty, int(len(bad)), detail, severity, _sample(bad))


# --- column checks: each takes (series, rule_value) and returns the offending values -----------

def _coerce(s: pd.Series, typ: str) -> pd.Series:
    if typ == "number":
        return pd.to_numeric(s, errors="coerce")
    if typ == "datetime":
        return pd.to_datetime(s, errors="coerce", utc=True)
    return s


def _type_bad(s: pd.Series, typ: str) -> pd.Series:
    nn = s.dropna()
    if typ in {"number", "datetime"}:
        return nn[_coerce(nn, typ).isna()]
    if typ == "integer":
        num = pd.to_numeric(nn, errors="coerce")
        return nn[num.isna() | (num % 1 != 0)]
    if typ == "boolean":
        return nn[~nn.astype(str).str.lower().isin({"true", "false", "1", "0", "yes", "no"})]
    return nn.iloc[0:0]  # string: anything goes


COLUMN_CHECKS: dict[str, Callable[[pd.Series, Any, dict], pd.Series]] = {
    "required": lambda s, v, r: s[s.isna() | (s.astype(str).str.strip() == "")] if v else s.iloc[0:0],
    "type": lambda s, v, r: _type_bad(s, v),
    "min": lambda s, v, r: s[_coerce(s, "number") < v],
    "max": lambda s, v, r: s[_coerce(s, "number") > v],
    "min_length": lambda s, v, r: s.dropna()[s.dropna().astype(str).str.len() < v],
    "max_length": lambda s, v, r: s.dropna()[s.dropna().astype(str).str.len() > v],
    "regex": lambda s, v, r: s.dropna()[~s.dropna().astype(str).str.fullmatch(v)],
    "allowed": lambda s, v, r: s.dropna()[~s.dropna().isin(v)],
    "unique": lambda s, v, r: s[s.duplicated(keep=False) & s.notna()] if v else s.iloc[0:0],
    "not_future": lambda s, v, r: s[_coerce(s, "datetime") > pd.Timestamp.now(tz="UTC")] if v else s.iloc[0:0],
}


def _null_pct(s: pd.Series, limit: float) -> CheckResult:
    pct = 100 * s.isna().mean() if len(s) else 0.0
    return CheckResult("max_null_pct", s.name, pct <= limit, int(s.isna().sum()),
                       f"{pct:.2f}% null (limit {limit}%)", "warn")


def _outliers(s: pd.Series, z: float) -> CheckResult:
    num = pd.to_numeric(s, errors="coerce").dropna()
    if len(num) < 8 or num.std(ddof=0) == 0:
        return CheckResult("outlier_z", s.name, True, detail="not enough variance", severity="warn")
    # Robust z-score (median / MAD) so the outliers don't hide themselves by inflating the std.
    med = num.median()
    mad = (num - med).abs().median() * 1.4826 or num.std(ddof=0)
    bad = num[((num - med) / mad).abs() > z]
    return _result("outlier_z", s.name, bad, f"robust |z| > {z}", "warn")


def _profile(df: pd.DataFrame) -> dict[str, dict]:
    out = {}
    for c in df.columns:
        s = df[c]
        p = {"dtype": str(s.dtype), "nulls": int(s.isna().sum()), "distinct": int(s.nunique(dropna=True))}
        if pd.api.types.is_numeric_dtype(s) and s.notna().any():
            p.update(min=float(s.min()), max=float(s.max()), mean=round(float(s.mean()), 4))
        out[str(c)] = p
    return out


def validate(df: pd.DataFrame, rules: dict, source: str = "<dataframe>") -> Report:
    results: list[CheckResult] = []
    table = rules.get("table", {}) or {}
    columns = rules.get("columns", {}) or {}

    if "min_rows" in table:
        results.append(CheckResult("min_rows", None, len(df) >= table["min_rows"], 0,
                                   f"{len(df)} rows (min {table['min_rows']})"))
    if "max_rows" in table:
        results.append(CheckResult("max_rows", None, len(df) <= table["max_rows"], 0,
                                   f"{len(df)} rows (max {table['max_rows']})"))
    if table.get("unique"):
        keys = table["unique"]
        missing = [k for k in keys if k not in df.columns]
        if missing:
            results.append(CheckResult("unique", ",".join(keys), False, detail=f"missing key columns {missing}"))
        else:
            dup = df[df.duplicated(subset=keys, keep=False)]
            results.append(CheckResult("unique", ",".join(keys), dup.empty, len(dup), "composite key",
                                       sample=dup[keys].head(5).astype(str).values.tolist()))
    if table.get("no_extra_columns"):
        extra = sorted(set(df.columns) - set(columns))
        results.append(CheckResult("no_extra_columns", None, not extra, len(extra), f"unexpected: {extra}"))

    for col, rule in columns.items():
        rule = rule or {}
        if col not in df.columns:
            sev = "error" if rule.get("required", True) else "warn"
            results.append(CheckResult("exists", col, False, detail="column missing", severity=sev))
            continue
        s = df[col]
        for name, fn in COLUMN_CHECKS.items():
            if name in rule:
                results.append(_result(name, col, fn(s, rule[name], rule), f"{name}={rule[name]!r}"))
        if "max_null_pct" in rule:
            results.append(_null_pct(s, rule["max_null_pct"]))
        if "outlier_z" in rule:
            results.append(_outliers(s, rule["outlier_z"]))

    return Report(source, len(df), df.shape[1], results, _profile(df))
