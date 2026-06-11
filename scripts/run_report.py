"""Week-5 evaluation: run 10 test queries, write report.md with cost accounting.

Needs GOOGLE_API_KEY. Writes report.md (summary + per-query detail) and
report/run.txt (full console transcript) at the repo root.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import config  # noqa: E402
from src.agent import Agent  # noqa: E402

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
    if not config.GOOGLE_API_KEY:
        print("GOOGLE_API_KEY not set — add it to .env (see .env.example).")
        return 1

    agent = Agent()
    transcript: list[str] = []
    rows = []

    for i, (q, role) in enumerate(QUERIES, 1):
        line = f"[{i}/10] ({role}) {q}"
        print(line)
        transcript.append(line)
        r = agent.query(q, user_role=role)
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


if __name__ == "__main__":
    sys.exit(main())
