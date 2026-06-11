"""CLI entrypoint for the TechCorp knowledge assistant.

    python app.py check                       # verify data + config
    python app.py ask "What is the PTO policy?" --role manager
"""
import argparse
import sys

from src import config
from src.agent import Agent


def cmd_check() -> int:
    ok = True
    for path in (config.DB_PATH, config.DOCUMENTS_PATH, config.POLICIES_PATH):
        present = path.exists()
        ok &= present
        print(f"  {'OK ' if present else 'MISS'}  {path.relative_to(config.ROOT)}")
    key = bool(config.GOOGLE_API_KEY)
    print(f"  {'OK ' if key else 'MISS'}  GOOGLE_API_KEY")
    print(f"  model: {config.MODEL}")
    if not ok:
        print("\n  data missing — run `make data`")
    return 0 if ok else 1


def cmd_ask(question: str, role: str) -> int:
    try:
        result = Agent().query(question, user_role=role)
    except ValueError as e:
        print(e)
        return 1
    for call in result.get("tool_calls", []):
        print(f"  → {call['tool']}({call['args']})")
    if result.get("tool_calls"):
        print()
    print(result["answer"])
    print(
        f"\n[{result['tokens_used']} tok "
        f"({result['input_tokens']} in / {result['output_tokens']} out) | "
        f"${result['cost']:.6f} | role={result['role']}]"
    )
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="TechCorp knowledge assistant")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("check", help="verify data files + config")
    ask = sub.add_parser("ask", help="ask one question")
    ask.add_argument("question")
    ask.add_argument("--role", default="engineer")

    args = ap.parse_args()
    if args.cmd == "check":
        sys.exit(cmd_check())
    elif args.cmd == "ask":
        sys.exit(cmd_ask(args.question, args.role))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
