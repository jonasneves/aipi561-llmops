"""Assemble report/report_print.html from report.json + the live-app
screenshots, ready for Chrome to print to report.pdf.

The screenshots in report/screenshots/questionNN.png are real captures of the
web UI (app_web.py) answering each query live — not rendered mockups.
Images are base64-embedded so the HTML is self-contained.
"""
import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "report" / "screenshots"


def img_tag(n: int) -> str:
    p = SHOTS / f"question{n:02d}.png"
    if not p.exists():
        return f"<p><em>(missing screenshot for query {n})</em></p>"
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f'<img src="data:image/png;base64,{b64}" alt="query {n} run">'


def main() -> int:
    data = json.loads((ROOT / "report.json").read_text())
    m = data["metrics"]
    rows = "".join(
        f"<tr><td>{q['n']}</td><td>{q['role']}</td><td>{q['query']}</td>"
        f"<td>{', '.join(c['tool'] for c in q['tool_calls']) or '—'}</td>"
        f"<td>{q['tokens_used']}</td><td>${q['cost']:.6f}</td></tr>"
        for q in data["queries"]
    )
    sections = "".join(
        f'<section class="q"><h3>{q["n"]}. {q["query"]}</h3>'
        f'<p class="role">role: {q["role"]} · live run via app_web.py</p>'
        f'{img_tag(q["n"])}</section>'
        for q in data["queries"]
    )
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>
  @page {{ margin: 1.4cm; }}
  body {{ font:14px/1.5 -apple-system,system-ui,sans-serif; color:#1d1d1f; }}
  h1 {{ color:#012169; margin:0 0 2px; }}
  h2 {{ color:#012169; border-bottom:2px solid #E2E6ED; padding-bottom:4px; margin-top:28px; }}
  .sub {{ color:#666; margin:0 0 18px; }}
  table {{ border-collapse:collapse; width:100%; font-size:12.5px; }}
  th,td {{ border:1px solid #E2E6ED; padding:6px 8px; text-align:left; vertical-align:top; }}
  th {{ background:#012169; color:#fff; }}
  .cost td:first-child {{ color:#666; width:200px; }} .cost {{ width:auto; }}
  .big {{ color:#012169; font-weight:700; }}
  .q {{ break-inside:avoid; margin-top:22px; }}
  .q h3 {{ margin:0 0 2px; font-size:15px; }}
  .role {{ color:#0577B1; font-size:12px; margin:0 0 8px; }}
  .q img {{ width:100%; border:1px solid #E2E6ED; border-radius:8px; }}
</style></head><body>
<h1>Week 5 — Evaluation Report</h1>
<p class="sub">TechCorp Knowledge Assistant · 10 test queries · {data['model']} on Vertex AI ·
  evidence = real screenshots of the agent UI (app_web.py)</p>

<h2>Cost summary</h2>
<table class="cost">
  <tr><td>Total queries</td><td class="big">{m['total_queries']}</td></tr>
  <tr><td>Total tokens</td><td>{m['total_tokens']:,}</td></tr>
  <tr><td>Total cost</td><td class="big">${m['total_cost']:.6f}</td></tr>
  <tr><td>Avg cost / query</td><td>${m['avg_cost_per_query']:.6f}</td></tr>
  <tr><td>Avg tokens / query</td><td>{m['avg_tokens_per_query']:,.0f}</td></tr>
</table>
<p class="sub">Rates (rubric): input ${data['rates']['input_per_1m']} / 1M,
  output ${data['rates']['output_per_1m']} / 1M tokens.</p>

<h2>Per-query results</h2>
<table>
  <tr><th>#</th><th>Role</th><th>Query</th><th>Tools called</th><th>Tokens</th><th>Cost</th></tr>
  {rows}
</table>

<h2>Test runs (screenshots)</h2>
{sections}
</body></html>"""
    out = ROOT / "report" / "report_print.html"
    out.write_text(doc)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
