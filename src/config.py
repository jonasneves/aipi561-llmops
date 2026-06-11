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

# Auth backend. Default is Vertex AI on the ops-ai-jonas GCP project — the same
# project Project 1 (aipi561-mlops) stands its GKE infra in. Vertex bills the
# Education credits directly via project quotas (no AI-Studio free-tier 20/day
# cap, which a sponsored billing account never escapes), so it's the durable
# path and aligns this repo with the shared infra. Auth flows from ADC
# (`gcloud auth application-default login`) — no API key needed.
# Set USE_VERTEX=0 to fall back to an AI-Studio API key (GOOGLE_API_KEY).
USE_VERTEX = os.getenv("USE_VERTEX", "1") not in ("0", "false", "")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "ops-ai-jonas")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")

# 2.5-flash is the workhorse the TA approved. Override via the MODEL env var.
MODEL = os.getenv("MODEL", "gemini-2.5-flash")

# Pricing (USD per 1M tokens) — figures fixed by the Week-5 rubric, not live
# list price. The cost-tracking mechanism is graded against these; cost claims
# trace here.
INPUT_COST_PER_1M = 0.075
OUTPUT_COST_PER_1M = 0.3
