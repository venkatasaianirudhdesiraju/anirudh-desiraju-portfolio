"""Command line: python -m loglens analyze logs/ [--md report.md] [--json] [--llm]"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .cluster import KnownIssues
from .core import analyze_texts, to_markdown


def _read_inputs(paths: list[str]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for p in map(Path, paths):
        files = sorted(x for x in p.rglob("*") if x.is_file()) if p.is_dir() else [p]
        for f in files:
            if f.suffix.lower() in {".log", ".txt", ".out", ".xml", ""} or p == f:
                texts[str(f)] = f.read_text(encoding="utf-8", errors="replace")
    return texts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="loglens", description="Cluster test failures into root causes.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze", help="analyze log files or folders")
    a.add_argument("paths", nargs="+")
    a.add_argument("--threshold", type=float, default=0.6, help="similarity to merge failures (0-1)")
    a.add_argument("--known", help="known-issues JSON file")
    a.add_argument("--llm", action="store_true", help="add local Ollama summaries for top clusters")
    a.add_argument("--json", action="store_true", help="print JSON instead of markdown")
    a.add_argument("--md", help="also write markdown report to this file")
    a.add_argument("--fail-on-new", action="store_true", help="exit 1 if any cluster is not a known issue")

    k = sub.add_parser("learn", help="record a cluster signature as a known issue")
    k.add_argument("--known", required=True)
    k.add_argument("--signature", required=True)
    k.add_argument("--ticket", required=True)
    k.add_argument("--notes", default="")

    args = ap.parse_args(argv)
    if args.cmd == "learn":
        KnownIssues(args.known).add(args.signature, args.ticket, args.notes)
        print(f"Saved {args.ticket} to {args.known}")
        return 0

    texts = _read_inputs(args.paths)
    if not texts:
        print("No log files found.", file=sys.stderr)
        return 2
    report = analyze_texts(texts, args.threshold, args.known, args.llm)
    md = to_markdown(report)
    if args.md:
        Path(args.md).write_text(md, encoding="utf-8")
    print(json.dumps(report, indent=2) if args.json else md)
    if args.fail_on_new and any(not c["known_issue"] for c in report["clusters"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
