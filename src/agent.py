"""The reasoning agent: Gemini picks a tool, observes, then loops or answers.

Uses google-genai native function-calling. The loop runs the model, executes
any tool calls it emits, feeds results back, and repeats until the model
answers in prose (or MAX_STEPS is hit). Cross-query accounting lands in phase 4.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from google import genai
from google.genai import types

from src import config
from src.tools import EmployeeLookupTool, ExpenseQueryTool, PolicySearchTool

logger = logging.getLogger(__name__)

MAX_STEPS = 5  # guard against a tool-call loop that never converges

_DECLARATIONS = [
    types.FunctionDeclaration(
        name="employee_lookup",
        description="Find an employee's record (department, title, salary, manager, "
        "etc.) by name or numeric ID from the HR database.",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "employee_name": types.Schema(
                    type="STRING", description="Full or partial name"
                ),
                "employee_id": types.Schema(
                    type="INTEGER", description="Exact employee ID"
                ),
            },
        ),
    ),
    types.FunctionDeclaration(
        name="policy_search",
        description="Search TechCorp policy documents (HR, finance, travel, PTO, "
        "security) and return the most relevant passages.",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "query": types.Schema(
                    type="STRING", description="What to look for"
                ),
                "limit": types.Schema(
                    type="INTEGER", description="Max documents (default 5)"
                ),
            },
            required=["query"],
        ),
    ),
    types.FunctionDeclaration(
        name="expense_query",
        description="Get the expense approval dollar limit for a role "
        "(ic1_ic2, ic3, manager, director, vp).",
        parameters=types.Schema(
            type="OBJECT",
            properties={"role": types.Schema(type="STRING", description="Role key")},
            required=["role"],
        ),
    ),
]


class Agent:
    """Answers TechCorp questions using Gemini + tools."""

    def __init__(self, db_path: str | None = None, api_key: str | None = None):
        self.db_path = db_path or str(config.DB_PATH)
        self.api_key = api_key or config.GOOGLE_API_KEY

        # Default: Vertex AI on the ops-ai-jonas project (ADC auth, bills credits,
        # no free-tier cap). Fallback: an AI-Studio API key. See config.py.
        if config.USE_VERTEX and not api_key:
            self.client = genai.Client(
                vertexai=True,
                project=config.GOOGLE_CLOUD_PROJECT,
                location=config.GOOGLE_CLOUD_LOCATION,
            )
        else:
            if not self.api_key:
                raise ValueError(
                    "No credentials. Either set USE_VERTEX=1 with ADC "
                    "(`gcloud auth application-default login`), or set "
                    "GOOGLE_API_KEY (https://aistudio.google.com/app/apikey)."
                )
            self.client = genai.Client(api_key=self.api_key)
        self.tools = {
            "employee_lookup": EmployeeLookupTool(self.db_path),
            "policy_search": PolicySearchTool(),
            "expense_query": ExpenseQueryTool(),
        }

        # metrics — cross-query accounting lands in phase 4
        self.total_tokens = 0
        self.total_cost = 0.0
        self.queries_run = 0

    def _build_system_prompt(self, user_role: str) -> str:
        tool_lines = "\n".join(
            f"- {t.name}: {t.description}" for t in self.tools.values()
        )
        return (
            "You are TechCorp's internal knowledge assistant. Answer employee "
            "questions about people, policies, and expenses.\n\n"
            "Use the tools below to ground every factual claim — never guess at "
            "a salary, policy detail, or limit. Call a tool, read the result, "
            "and call more tools if you need them. When you have enough, answer "
            "in clear prose and cite the policy title or record you used.\n\n"
            f"Available tools:\n{tool_lines}\n\n"
            f"The user's role is: {user_role}."
        )

    def _run_tool(self, name: str, args: dict) -> str:
        tool = self.tools.get(name)
        if tool is None:
            return f"Error: unknown tool {name}"
        logger.info("tool %s(%s)", name, args)
        return tool.execute(**args)

    def query(self, user_query: str, user_role: str = "engineer") -> Dict[str, Any]:
        logger.info("query: %s (role=%s)", user_query, user_role)
        cfg = types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=_DECLARATIONS)],
            system_instruction=self._build_system_prompt(user_role),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
            temperature=0,
        )
        contents: List[types.Content] = [
            types.Content(role="user", parts=[types.Part(text=user_query)])
        ]

        in_tokens = out_tokens = 0
        trace: List[Dict[str, Any]] = []
        answer = ""

        for _ in range(MAX_STEPS):
            resp = self.client.models.generate_content(
                model=config.MODEL, contents=contents, config=cfg
            )
            usage = resp.usage_metadata
            in_tokens += getattr(usage, "prompt_token_count", 0) or 0
            out_tokens += getattr(usage, "candidates_token_count", 0) or 0

            calls = resp.function_calls or []
            if not calls:
                text = (resp.text or "").strip()
                if text:
                    answer = text
                    break
                # empty turn (e.g. thinking-only) — nudge once for the answer
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part(text="Now give your final answer to "
                                          "the question, using the results above.")],
                    )
                )
                continue

            contents.append(resp.candidates[0].content)  # model's tool-call turn
            responses = []
            for fc in calls:
                result = self._run_tool(fc.name, dict(fc.args or {}))
                trace.append({"tool": fc.name, "args": dict(fc.args or {}), "result": result})
                responses.append(
                    types.Part.from_function_response(
                        name=fc.name, response={"result": result}
                    )
                )
            contents.append(types.Content(role="user", parts=responses))
        else:
            answer = answer or "Stopped: reached the tool-call step limit."

        cost = self._estimate_query_cost(in_tokens, out_tokens)
        self.queries_run += 1
        self.total_tokens += in_tokens + out_tokens
        self.total_cost += cost
        return {
            "answer": answer,
            "tokens_used": in_tokens + out_tokens,
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "cost": cost,
            "role": user_role,
            "tool_calls": trace,
        }

    def _estimate_query_cost(self, input_tokens: int, output_tokens: int) -> float:
        return (
            input_tokens / 1_000_000 * config.INPUT_COST_PER_1M
            + output_tokens / 1_000_000 * config.OUTPUT_COST_PER_1M
        )

    def get_metrics(self) -> Dict[str, Any]:
        n = self.queries_run
        return {
            "total_queries": n,
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 6),
            "avg_cost_per_query": round(self.total_cost / n, 6) if n else 0.0,
            "avg_tokens_per_query": round(self.total_tokens / n, 1) if n else 0.0,
        }
