"""Tools the agent can call. Each exposes execute(**kwargs) -> str."""
from __future__ import annotations

import json
import logging
import math
import re
import sqlite3
from collections import Counter

from src import config

logger = logging.getLogger(__name__)

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


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
        if not employee_name and not employee_id:
            return "Provide employee_name or employee_id."
        try:
            con = sqlite3.connect(self.db_path)
            con.row_factory = sqlite3.Row
            try:
                cur = con.cursor()
                if employee_id is not None:
                    cur.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
                else:
                    cur.execute(
                        "SELECT * FROM employees WHERE name LIKE ? LIMIT 5",
                        (f"%{employee_name}%",),
                    )
                rows = [dict(r) for r in cur.fetchall()]
            finally:
                con.close()
        except Exception as e:  # noqa: BLE001 — surface DB errors to the agent
            logger.error("Employee lookup error: %s", e)
            return f"Error: {e}"
        if not rows:
            return "Employee not found"
        return json.dumps(rows if len(rows) > 1 else rows[0], indent=2, default=str)


class PolicySearchTool(Tool):
    """Retrieve policy documents by TF-IDF cosine relevance to a query."""

    def __init__(self):
        super().__init__("policy_search", "Search policy documents by keyword or topic")
        self.documents: list[dict] = json.loads(config.DOCUMENTS_PATH.read_text())
        self.idf: dict[str, float] = {}
        self._vectors: list[dict[str, float]] = self._build_index()

    def _build_index(self) -> list[dict[str, float]]:
        n = len(self.documents)
        tfs, df = [], Counter()
        for doc in self.documents:
            tf = Counter(_tokenize(f"{doc.get('title','')} {doc.get('content','')}"))
            tfs.append(tf)
            df.update(tf.keys())
        self.idf = {t: math.log((1 + n) / (1 + c)) + 1.0 for t, c in df.items()}
        return [self._normalize(self._weight(tf)) for tf in tfs]

    def _weight(self, tf: Counter) -> dict[str, float]:
        return {t: (1 + math.log(f)) * self.idf.get(t, 0.0) for t, f in tf.items()}

    @staticmethod
    def _normalize(vec: dict[str, float]) -> dict[str, float]:
        norm = math.sqrt(sum(w * w for w in vec.values())) or 1.0
        return {t: w / norm for t, w in vec.items()}

    def execute(self, query: str, limit: int = 5) -> str:
        try:
            qv = self._normalize(self._weight(Counter(_tokenize(query))))
            scored = [
                (sum(w * dv.get(t, 0.0) for t, w in qv.items()), i)
                for i, dv in enumerate(self._vectors)
            ]
            scored = sorted((s for s in scored if s[0] > 0), reverse=True)[:limit]
            if not scored:
                return f"No policy documents matched: {query}"
            blocks = []
            for score, i in scored:
                doc = self.documents[i]
                snippet = " ".join(doc.get("content", "").split())[:500]
                blocks.append(
                    f"[{doc['title']}] "
                    f"(relevance {score:.2f} · {doc.get('category','')}/"
                    f"{doc.get('sensitivity','')})\n{snippet}"
                )
            return "\n\n".join(blocks)
        except Exception as e:  # noqa: BLE001
            logger.error("Policy search error: %s", e)
            return f"Error: {e}"


class ExpenseQueryTool(Tool):
    """Look up expense approval limits by role."""

    def __init__(self):
        super().__init__("expense_query", "Query expense approval limits by role")
        self.policies: dict = json.loads(config.POLICIES_PATH.read_text())

    def execute(self, role: str) -> str:
        try:
            limits = self.policies.get("expense", {}).get("approval_limits", {})
            if role not in limits:
                return f"Role not found: {role}. Known roles: {', '.join(limits)}"
            return f"Approval limit for {role}: ${limits[role]:,}"
        except Exception as e:  # noqa: BLE001
            logger.error("Expense query error: %s", e)
            return f"Error: {e}"
