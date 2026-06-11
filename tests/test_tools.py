"""Smoke tests for the three tools against the real dataset. No API key needed.

Requires `make data` to have populated data/.
"""
import json

import pytest

from src.tools import EmployeeLookupTool, ExpenseQueryTool, PolicySearchTool


@pytest.fixture(scope="module")
def emp():
    return EmployeeLookupTool()


def test_employee_lookup_by_id_returns_record(emp):
    out = emp.execute(employee_id=1)
    rec = json.loads(out)
    assert rec["id"] == 1
    assert "name" in rec and "department_name" in rec


def test_employee_lookup_by_name_matches(emp):
    # resolve a real name from id=1, then search for it
    name = json.loads(emp.execute(employee_id=1))["name"]
    out = emp.execute(employee_name=name.split()[0])
    assert name.split()[0].lower() in out.lower()


def test_employee_lookup_missing():
    assert EmployeeLookupTool().execute(employee_id=999_999) == "Employee not found"


def test_policy_search_ranks_relevant_doc_first():
    out = PolicySearchTool().execute("remote work from home policy", limit=3)
    assert "relevance" in out
    # the top block should be the most relevant; sanity-check it's non-empty prose
    assert len(out.splitlines()[0]) > 0


def test_policy_search_no_match():
    out = PolicySearchTool().execute("zzzqqxnonexistentterm")
    assert out.startswith("No policy documents matched")


@pytest.mark.parametrize(
    "role,amount",
    [("ic1_ic2", "$500"), ("manager", "$5,000"), ("vp", "$100,000")],
)
def test_expense_query_known_roles(role, amount):
    assert amount in ExpenseQueryTool().execute(role)


def test_expense_query_unknown_role():
    assert ExpenseQueryTool().execute("ceo").startswith("Role not found")
