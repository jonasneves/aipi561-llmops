"""Pull the course dataset into data/ (git-ignored, ~50MB).

Source: AIPI-561-Operationalizing-AI/Ops-AI-Student/week5/data.
The DB is too large to commit, so this fetches it on demand.
"""
import urllib.request
from pathlib import Path

BASE = (
    "https://raw.githubusercontent.com/AIPI-561-Operationalizing-AI/"
    "Ops-AI-Student/main/week5/data"
)
FILES = ["techcorp.db", "documents.json", "policies.json", "access_control.json"]
DATA = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    DATA.mkdir(exist_ok=True)
    for name in FILES:
        dest = DATA / name
        print(f"  downloading {name} ...", end=" ", flush=True)
        urllib.request.urlretrieve(f"{BASE}/{name}", dest)
        print(f"{dest.stat().st_size:,} bytes")
    print(f"done → {DATA}")


if __name__ == "__main__":
    main()
