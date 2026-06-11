"""Tools the agent can call. Each exposes execute(**kwargs) -> str.

Phase 1 lands the class surface with stub bodies; phase 2 fills execute().
"""
from __future__ import annotations

import logging

from src import config

logger = logging.getLogger(__name__)

_STUB = "not implemented yet (phase 2)"


class Tool:
    """Base class for tools the agent can call."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute(self, **kwargs) -> str:
        raise NotImplementedError


class EmployeeLookupTool(Tool):
    """Look up employee records from the SQLite database."""

    def __init__(self, db_path: str | None = None):
        super().__init__("employee_lookup", "Find employee information by name or ID")
        self.db_path = db_path or str(config.DB_PATH)

    def execute(self, employee_name: str = None, employee_id: str = None) -> str:
        return _STUB


class PolicySearchTool(Tool):
    """Retrieve policy documents by semantic relevance to a query."""

    def __init__(self):
        super().__init__("policy_search", "Search policy documents by keyword or topic")
        self.documents: list[dict] = []

    def execute(self, query: str, limit: int = 5) -> str:
        return _STUB


class ExpenseQueryTool(Tool):
    """Look up expense approval limits by role."""

    def __init__(self):
        super().__init__("expense_query", "Query expense approval limits by role")
        self.policies: dict = {}

    def execute(self, role: str) -> str:
        return _STUB
