"""Central config: model, pricing, paths. Single source of truth."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "techcorp.db"
DOCUMENTS_PATH = DATA_DIR / "documents.json"
POLICIES_PATH = DATA_DIR / "policies.json"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# gemini-2.5-flash: the free-tier model. (2.5-pro is billing-only now —
# free tier returns limit:0.) The reasoning loop and tool-use are identical.
MODEL = "gemini-2.5-flash"

# Pricing (USD per 1M tokens) — figures fixed by the Week-5 rubric, not live
# list price. The cost-tracking mechanism is graded against these; cost claims
# trace here.
INPUT_COST_PER_1M = 0.075
OUTPUT_COST_PER_1M = 0.3
