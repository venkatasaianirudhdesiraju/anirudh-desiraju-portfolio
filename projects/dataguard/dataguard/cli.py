"""python -m dataguard check data.csv --rules rules.yaml [--html report.html] [--json]"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import warnings

import pandas as pd

warnings.filterwarnings("ignore", message="Could not infer format")
import yaml

from .engine import load_rules, load_table, validate
from .report import to_html


def infer_rules(df: pd.DataFrame) -> dict:
    """Bootstrap a rules file from a known-good dataset."""
    cols = {}
    for c in df.columns:
        s = df[c]
        r: dict = {"required": bool(s.notna().all())}
        if pd.api.types.is_bool_dtype(s):
            r["type"] = "boolean"
        elif pd.api.types.is_numeric_dtype(s):
            r.update(type="number", min=float(s.min()), max=float(s.max()))
        elif pd.to_datetime(s, errors="coerce").notna().mean() > 0.95:
            r["type"] = "datetime"
        else:
            r["type"] = "string"
            if 0 < s.nunique() <= 12 and len(s) >= 20:
                r["allowed"] = sorted(map(str, s.dropna().unique()))
        if s.is_unique and s.notna().all():
            r["unique"] = True
        cols[str(c)] = r
    return {"table": {"min_rows": 1}, "columns": cols}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="dataguard")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("data")
    c.add_argument("--rules", required=True)
    c.add_argument("--html")
    c.add_argument("--json", action="store_true")
    c.add_argument("--strict", action="store_true", help="treat warnings as failures")
    i = sub.add_parser("infer", help="generate a starter rules.yaml from a good dataset")
    i.add_argument("data")
    i.add_argument("-o", "--out", default="rules.yaml")
    args = ap.parse_args(argv)

    df = load_table(args.data)
    if args.cmd == "infer":
        Path(args.out).write_text(yaml.safe_dump(infer_rules(df), sort_keys=False), encoding="utf-8")
        print(f"Wrote {args.out}")
        return 0

    report = validate(df, load_rules(args.rules), args.data)
    if args.html:
        Path(args.html).write_text(to_html(report), encoding="utf-8")
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, default=str))
    else:
        print(f"{'PASSED' if report.passed else 'FAILED'}  score={report.score}%  "
              f"errors={len(report.errors)}  warnings={len(report.warnings)}  rows={report.rows}")
        for r in report.errors + report.warnings:
            print(f"  [{r.severity.upper()}] {r.column or 'table'}.{r.check}: {r.failed_rows} bad — {r.detail} {r.sample[:3]}")
    failed = not report.passed or (args.strict and report.warnings)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
