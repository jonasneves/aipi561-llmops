"""Cost/metrics accounting tests. Fakes the Gemini client — no API key needed."""
from types import SimpleNamespace

import pytest

from src import config
from src.agent import Agent


class _FakeModels:
    """Returns a no-tool-call response with fixed token usage."""

    def __init__(self, prompt_tok, cand_tok):
        self._usage = SimpleNamespace(
            prompt_token_count=prompt_tok, candidates_token_count=cand_tok
        )

    def generate_content(self, **kwargs):
        return SimpleNamespace(
            usage_metadata=self._usage,
            function_calls=[],
            text="ok",
            candidates=[],
        )


@pytest.fixture
def agent(monkeypatch):
    monkeypatch.setattr(config, "GOOGLE_API_KEY", "test-key")
    a = Agent(api_key="test-key")
    a.client = SimpleNamespace(models=_FakeModels(prompt_tok=1000, cand_tok=500))
    return a


def test_estimate_cost_matches_rubric_rates(agent):
    # 1M input @ $0.075 + 1M output @ $0.30
    assert agent._estimate_query_cost(1_000_000, 0) == pytest.approx(0.075)
    assert agent._estimate_query_cost(0, 1_000_000) == pytest.approx(0.30)


def test_query_reports_and_accumulates(agent):
    r = agent.query("hi")
    assert r["tokens_used"] == 1500
    assert r["input_tokens"] == 1000 and r["output_tokens"] == 500
    # 1000/1e6*0.075 + 500/1e6*0.3 = 0.000075 + 0.00015
    assert r["cost"] == pytest.approx(0.000225)


def test_metrics_average_over_queries(agent):
    for _ in range(4):
        agent.query("hi")
    m = agent.get_metrics()
    assert m["total_queries"] == 4
    assert m["total_tokens"] == 6000
    assert m["avg_cost_per_query"] == pytest.approx(0.000225)
    assert m["avg_tokens_per_query"] == pytest.approx(1500.0)


def test_metrics_empty_is_safe():
    import src.agent as ag

    a = Agent.__new__(Agent)  # no API call
    a.queries_run = a.total_tokens = 0
    a.total_cost = 0.0
    assert a.get_metrics()["avg_cost_per_query"] == 0.0
