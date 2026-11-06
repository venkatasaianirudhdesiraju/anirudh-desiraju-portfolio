"""python -m jobfit resume.pdf job.txt [--tailor] [--json]"""
from __future__ import annotations

import argparse
import json

from .io import read_text
from .llm import tailor
from .scoring import score


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="jobfit")
    ap.add_argument("resume")
    ap.add_argument("jobs", nargs="+", help="one or more job description files (ranked if several)")
    ap.add_argument("--tailor", action="store_true", help="draft tailored bullets with local Ollama")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    resume = read_text(a.resume)
    results = sorted(((score(resume, read_text(j)), j) for j in a.jobs), key=lambda x: -x[0].score)
    if a.json:
        print(json.dumps([{"job": j, **r.to_dict()} for r, j in results], indent=2))
        return 0
    for r, j in results:
        print(f"\n=== {j}: {r.score}% fit  (skills {r.skill_coverage}%, similarity {r.semantic_similarity}) ===")
        print("Matched:          ", ", ".join(r.matched) or "—")
        print("Missing required: ", ", ".join(r.missing_required) or "—")
        print("Missing preferred:", ", ".join(r.missing_preferred) or "—")
        print("Keyword gaps:     ", ", ".join(r.keyword_gaps) or "—")
        for s in r.suggestions:
            print("  •", s)
    if a.tailor:
        best = results[0][1]
        print(f"\n--- Tailored draft for {best} ---\n" + (tailor(resume, read_text(best)) or "Ollama not reachable."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
