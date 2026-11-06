"""Self-contained HTML report (no external assets) — attach it to CI artifacts or email it."""
from __future__ import annotations

import html

from .engine import Report


def to_html(report: Report) -> str:
    color = "#16a34a" if report.passed else "#dc2626"
    rows = []
    for r in sorted(report.results, key=lambda r: (r.passed, r.severity != "error")):
        status = "PASS" if r.passed else ("FAIL" if r.severity == "error" else "WARN")
        cls = status.lower()
        rows.append(
            f"<tr class='{cls}'><td>{status}</td><td>{html.escape(r.column or 'table')}</td>"
            f"<td>{html.escape(r.check)}</td><td>{r.failed_rows}</td><td>{html.escape(r.detail)}</td>"
            f"<td><code>{html.escape(str(r.sample)[:200]) if r.sample else ''}</code></td></tr>"
        )
    prof = "".join(
        f"<tr><td>{html.escape(c)}</td><td>{p['dtype']}</td><td>{p['nulls']}</td><td>{p['distinct']}</td>"
        f"<td>{p.get('min', '')}</td><td>{p.get('max', '')}</td><td>{p.get('mean', '')}</td></tr>"
        for c, p in report.profile.items()
    )
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>DataGuard — {html.escape(report.source)}</title>
<style>
body{{font:14px system-ui,sans-serif;margin:2rem;color:#111}} h1{{margin:0}}
.badge{{display:inline-block;padding:.3rem .8rem;border-radius:999px;color:#fff;background:{color};font-weight:600}}
.kpis{{display:flex;gap:1rem;margin:1rem 0}} .kpi{{border:1px solid #e5e7eb;border-radius:8px;padding:.6rem 1rem}}
.kpi b{{display:block;font-size:1.4rem}} table{{border-collapse:collapse;width:100%;margin:1rem 0}}
td,th{{border-bottom:1px solid #e5e7eb;padding:.4rem;text-align:left;vertical-align:top}}
tr.fail td:first-child{{color:#dc2626;font-weight:700}} tr.warn td:first-child{{color:#d97706;font-weight:700}}
tr.pass td:first-child{{color:#16a34a}} code{{font-size:12px}}
</style></head><body>
<h1>DataGuard report</h1><p>{html.escape(report.source)}</p>
<span class="badge">{'PASSED' if report.passed else 'FAILED'}</span>
<div class="kpis"><div class="kpi"><b>{report.score}%</b>checks passed</div>
<div class="kpi"><b>{len(report.errors)}</b>errors</div><div class="kpi"><b>{len(report.warnings)}</b>warnings</div>
<div class="kpi"><b>{report.rows:,}</b>rows × {report.columns} cols</div></div>
<h2>Checks</h2><table><tr><th>Status</th><th>Column</th><th>Check</th><th>Bad rows</th><th>Detail</th><th>Sample</th></tr>
{''.join(rows)}</table>
<h2>Profile</h2><table><tr><th>Column</th><th>Type</th><th>Nulls</th><th>Distinct</th><th>Min</th><th>Max</th><th>Mean</th></tr>
{prof}</table></body></html>"""
