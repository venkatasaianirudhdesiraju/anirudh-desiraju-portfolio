"""High-level analyze() used by both the CLI and the API."""
from __future__ import annotations

from pathlib import Path

from .cluster import Cluster, KnownIssues, cluster_failures
from .parser import extract_failures
from . import llm


def analyze_texts(
    texts: dict[str, str],
    threshold: float = 0.6,
    known_issues: str | Path | None = None,
    use_llm: bool = False,
    llm_top: int = 5,
) -> dict:
    failures = []
    for source, text in texts.items():
        failures.extend(extract_failures(text, source))
    clusters = cluster_failures(failures, threshold)
    KnownIssues(known_issues).match(clusters)

    llm_used = False
    if use_llm and clusters and llm.ollama_available():
        for c in clusters[:llm_top]:
            c.summary = llm.summarize(c)
            llm_used = llm_used or c.summary is not None

    return {
        "total_failures": len(failures),
        "unique_root_causes": len(clusters),
        "known": sum(1 for c in clusters if c.known_issue),
        "llm_used": llm_used,
        "clusters": [c.to_dict() for c in clusters],
    }


def to_markdown(report: dict) -> str:
    out = [
        "# LogLens failure report",
        "",
        f"**{report['total_failures']}** failures → **{report['unique_root_causes']}** distinct root causes "
        f"({report['known']} already known).",
        "",
        "| # | Failures | Headline | Known issue |",
        "|---|---:|---|---|",
    ]
    for c in report["clusters"]:
        ki = c["known_issue"]["ticket"] if c["known_issue"] else "—"
        out.append(f"| {c['id']} | {c['count']} | `{c['headline'][:90]}` | {ki} |")
    for c in report["clusters"]:
        out += ["", f"## #{c['id']} — {c['count']} failure(s)", "", f"`{c['headline']}`", ""]
        out.append("**Tests:** " + ", ".join(c["tests"][:15]) + (" …" if len(c["tests"]) > 15 else ""))
        if c["known_issue"]:
            ki = c["known_issue"]
            out.append(f"\n**Known issue:** {ki['ticket']} (similarity {ki['similarity']}) — {ki.get('notes', '')}")
        if c["summary"]:
            out += ["", "**AI triage:**", "", c["summary"]]
        out += ["", "<details><summary>Signature</summary>", "", "```", c["signature"], "```", "</details>"]
    return "\n".join(out) + "\n"
