"""The reasoning agent: Gemini picks a tool, observes, then loops or answers.

Phase 1 wires the tool registry and the result contract; phase 3 adds the
reasoning loop, phase 4 the cost/metric accounting.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from src import config
from src.tools import EmployeeLookupTool, ExpenseQueryTool, PolicySearchTool

logger = logging.getLogger(__name__)


class Agent:
    """Answers TechCorp questions using Gemini + tools."""

    def __init__(self, db_path: str | None = None, api_key: str | None = None):
        self.db_path = db_path or str(config.DB_PATH)
        self.api_key = api_key or config.GOOGLE_API_KEY

        self.tools = {
            "employee_lookup": EmployeeLookupTool(self.db_path),
            "policy_search": PolicySearchTool(),
            "expense_query": ExpenseQueryTool(),
        }

        # metrics — populated in phase 4
        self.total_tokens = 0
        self.total_cost = 0.0
        self.queries_run = 0

    def query(self, user_query: str, user_role: str = "engineer") -> Dict[str, Any]:
        logger.info("query: %s (role=%s)", user_query, user_role)
        # reasoning loop — phase 3
        return {
            "answer": "not implemented yet (phase 3)",
            "tokens_used": 0,
            "cost": 0.0,
            "role": user_role,
        }

    def _estimate_query_cost(self, input_tokens: int, output_tokens: int) -> float:
        return (
            input_tokens / 1_000_000 * config.INPUT_COST_PER_1M
            + output_tokens / 1_000_000 * config.OUTPUT_COST_PER_1M
        )

    def get_metrics(self) -> Dict[str, Any]:
        # accounting — phase 4
        return {
            "total_queries": self.queries_run,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "avg_cost_per_query": 0.0,
        }
