"""Markdown + standalone HTML daily report."""
from __future__ import annotations

import html

DISCLAIMER = ("Research output from a statistical model, not financial advice. Confidence = how often similar "
              "signals were right in out-of-sample testing. Past performance does not predict future results. "
              "Paper trade first; never risk money you can't afford to lose.")


def to_markdown(res: dict) -> str:
    m = res["model"]
    out = [f"# TradeScout — top {len(res['picks'])} for {res['date']}", "",
           f"Account ${res['account']:,.0f} · horizon {m['horizon']} day(s) · model trained {m['trained_at']}", "",
           f"> **Model health:** {m['verdict']}", "",
           "| # | Ticker | Position | Confidence | Price | Stop | Target | Shares | $ | % acct | Why |",
           "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for i, p in enumerate(res["picks"], 1):
        out.append(f"| {i} | **{p['ticker']}** | {p['side']} | {p['confidence']}% | {p['price']} | {p['stop']} | "
                   f"{p['target']} | {p['shares']} | {p['dollars']:,.0f} | {p['pct_of_account']}% | {p['why']} |")
    out += ["", "## Calibration (out-of-sample)", "", "| Model confidence | Times | Actually right |", "|---|---:|---:|"]
    out += [f"| {r['confidence']} | {r['n']:,} | {100*r['hit_rate']:.1f}% |" for r in m["calibration_table"]]
    bt = m["backtest"]
    if bt.get("days"):
        out += ["", f"**Backtest {bt['period'][0]} → {bt['period'][1]}:** {bt['trades']:,} trades, win rate "
                f"{100*bt['win_rate']:.1f}%, avg {bt['avg_trade_ret_pct']}%/trade, Sharpe {bt['sharpe']}, "
                f"max drawdown {bt['max_drawdown_pct']}% (after {5} bps/side costs)."]
    heads = [(p["ticker"], h) for p in res["picks"] for h in p["headlines"]]
    if heads:
        out += ["", "## Headlines driving sentiment", ""]
        out += [f"- **{t}** ({h['score']:+.2f}, {h['source']}): [{h['title']}]({h['url']})" for t, h in heads]
    out += ["", f"_{DISCLAIMER}_"]
    return "\n".join(out) + "\n"


def to_html(res: dict) -> str:
    m = res["model"]
    rows = "".join(
        f"<tr><td>{i}</td><td><b>{p['ticker']}</b></td><td class='{p['side'].lower()}'>{p['side']}</td>"
        f"<td><div class='bar'><span style='width:{(p['confidence']-50)*2:.0f}%'></span></div>{p['confidence']}%</td>"
        f"<td>{p['price']}</td><td>{p['stop']}</td><td>{p['target']}</td><td>{p['shares']}</td>"
        f"<td>${p['dollars']:,.0f}</td><td>{p['pct_of_account']}%</td><td>{html.escape(p['why'])}</td></tr>"
        for i, p in enumerate(res["picks"], 1))
    edge_cls = "ok" if m["has_edge"] else "warn"
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TradeScout {res['date']}</title><style>
body{{font:14px system-ui,sans-serif;margin:1.5rem;color:#111;background:#fafafa}} table{{border-collapse:collapse;width:100%;background:#fff}}
td,th{{padding:.45rem;border-bottom:1px solid #eee;text-align:left}} .long{{color:#15803d;font-weight:700}} .short{{color:#b91c1c;font-weight:700}}
.bar{{display:inline-block;width:60px;height:8px;background:#eee;border-radius:4px;margin-right:6px;vertical-align:middle}}
.bar span{{display:block;height:8px;background:#2563eb;border-radius:4px}} .health{{padding:.8rem 1rem;border-radius:8px;margin:1rem 0}}
.ok{{background:#dcfce7}} .warn{{background:#fef3c7}} small{{color:#666}}
</style></head><body><h1>TradeScout — {res['date']}</h1>
<small>Account ${res['account']:,.0f} · horizon {m['horizon']}d · trained {m['trained_at']}</small>
<div class="health {edge_cls}"><b>Model health:</b> {html.escape(m['verdict'])}</div>
<table><tr><th>#</th><th>Ticker</th><th>Position</th><th>Confidence</th><th>Price</th><th>Stop</th><th>Target</th>
<th>Shares</th><th>Size</th><th>% acct</th><th>Why</th></tr>{rows}</table>
<p><small>{DISCLAIMER}</small></p></body></html>"""
