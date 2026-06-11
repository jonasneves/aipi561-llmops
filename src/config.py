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

MODEL = "gemini-2.5-pro"

# Gemini 2.5 Pro pricing (USD per 1M tokens) — figures fixed by the
# Week-5 rubric, not live list price. Cost claims trace here.
INPUT_COST_PER_1M = 0.075
OUTPUT_COST_PER_1M = 0.3
