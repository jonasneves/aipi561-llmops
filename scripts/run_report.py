"""Week-5 evaluation: run 10 test queries, write report.md with cost accounting.

Auth via Vertex AI (default) or GOOGLE_API_KEY — see config.py. Writes
report.md (summary + per-query detail), report.json (structured trace for the
visualizer / screenshots), and report/run.txt (full console transcript).
"""
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from google.genai import errors  # noqa: E402

from src import config  # noqa: E402
from src.agent import Agent  # noqa: E402

# Free-tier Flash allows 5 requests/min; each query is ~2 model calls. Pace
# query starts so a 10-query run stays under the limit.
PACE_SECONDS = int(os.getenv("REPORT_PACE_SECONDS", "30"))


_RETRYABLE = {429, 503}  # rate-limited / transient server overload


def _query_with_retry(agent, q, role, attempts: int = 4):
    """Run one query, retrying transient 429/503 with escalating backoff."""
    for attempt in range(1, attempts + 1):
        try:
            return agent.query(q, user_role=role)
        except errors.APIError as e:
            if getattr(e, "code", None) not in _RETRYABLE or attempt == attempts:
                raise
            wait = 20 * attempt
            print(f"    {e.code}; retry {attempt}/{attempts - 1} in {wait}s ...")
            time.sleep(wait)

# (question, role) — spans all three tools, multi-tool reasoning, and roles.
QUERIES = [
    ("What is the PTO policy, and how many days do managers get?", "engineer"),
    ("What's the expense approval limit for a manager?", "engineer"),
    ("Look up the employee with ID 1 — name, title, and department.", "manager"),
    ("What does the travel policy say about international flight limits?", "engineer"),
    ("Find an employee whose name contains 'Smith'.", "manager"),
    (
        "What's the approval limit for a director, and does policy require a "
        "receipt for a $30 expense?",
        "manager",
    ),
    ("What is the company's security or data-handling policy?", "engineer"),
    ("What is employee 100's title and department?", "manager"),
    ("What is the expense submission deadline, per policy?", "engineer"),
    ("Compare the expense approval limits for ic3 versus vp.", "manager"),
]


def main() -> int:
    if not config.USE_VERTEX and not config.GOOGLE_API_KEY:
        print("No credentials — set USE_VERTEX=1 (ADC) or GOOGLE_API_KEY "
              "(see .env.example).")
        return 1

    agent = Agent()
    transcript: list[str] = []
    rows = []

    for i, (q, role) in enumerate(QUERIES, 1):
        if i > 1:
            time.sleep(PACE_SECONDS)  # stay under the 5 req/min free-tier limit
        line = f"[{i}/10] ({role}) {q}"
        print(line)
        transcript.append(line)
        r = _query_with_retry(agent, q, role)
        for c in r["tool_calls"]:
            t = f"    -> {c['tool']}({c['args']})"
            print(t)
            transcript.append(t)
        meta = (
            f"    {r['tokens_used']} tok "
            f"({r['input_tokens']} in / {r['output_tokens']} out) "
            f"= ${r['cost']:.6f}"
        )
        print(meta)
        transcript.append(meta)
        transcript.append(f"    ANSWER: {r['answer']}")
        rows.append((i, q, role, r))

    metrics = agent.get_metrics()
    _write_report(rows, metrics)
    _write_json(rows, metrics)
    (ROOT / "report").mkdir(exist_ok=True)
    (ROOT / "report" / "run.txt").write_text("\n".join(transcript) + "\n")
    print(f"\nTotal: {metrics['total_queries']} queries, "
          f"{metrics['total_tokens']} tokens, ${metrics['total_cost']:.6f}")
    print(f"wrote {ROOT/'report.md'} and {ROOT/'report'/'run.txt'}")
    return 0


def _write_report(rows, m) -> None:
    out = ["# Week 5 — Evaluation Report\n",
           "TechCorp Knowledge Assistant · 10 test queries against "
           f"`{config.MODEL}`.\n",
           "## Cost summary\n",
           "| Metric | Value |",
           "|---|---|",
           f"| Total queries | {m['total_queries']} |",
           f"| Total tokens | {m['total_tokens']:,} |",
           f"| **Total cost** | **${m['total_cost']:.6f}** |",
           f"| Avg cost / query | ${m['avg_cost_per_query']:.6f} |",
           f"| Avg tokens / query | {m['avg_tokens_per_query']:,.0f} |",
           "\nRates (rubric): input $0.075 / 1M, output $0.30 / 1M tokens.\n",
           "## Per-query results\n",
           "| # | Role | Query | Tools called | Tokens | Cost |",
           "|---|---|---|---|---|---|"]
    for i, q, role, r in rows:
        tools = ", ".join(c["tool"] for c in r["tool_calls"]) or "—"
        out.append(
            f"| {i} | {role} | {q} | {tools} | {r['tokens_used']} | "
            f"${r['cost']:.6f} |"
        )
    out.append("\n## Answers\n")
    for i, q, role, r in rows:
        tools = ", ".join(c["tool"] for c in r["tool_calls"]) or "none"
        out.append(f"### {i}. {q}")
        out.append(f"*Role: {role} · tools: {tools}*\n")
        out.append(f"{r['answer']}\n")
    (ROOT / "report.md").write_text("\n".join(out) + "\n")


def _write_json(rows, m) -> None:
    """Structured trace — the data source for screenshots, PDF, and viz."""
    data = {
        "model": config.MODEL,
        "rates": {
            "input_per_1m": config.INPUT_COST_PER_1M,
            "output_per_1m": config.OUTPUT_COST_PER_1M,
        },
        "metrics": m,
        "queries": [
            {
                "n": i,
                "query": q,
                "role": role,
                "answer": r["answer"],
                "input_tokens": r["input_tokens"],
                "output_tokens": r["output_tokens"],
                "tokens_used": r["tokens_used"],
                "cost": r["cost"],
                "tool_calls": r["tool_calls"],  # [{tool, args, result}]
            }
            for i, q, role, r in rows
        ],
    }
    (ROOT / "report.json").write_text(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    sys.exit(main())
