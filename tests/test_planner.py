import json
from types import SimpleNamespace

import pytest

from operations_copilot.config import Settings
from operations_copilot.planner import (
    HeuristicPlanner,
    OpenAICompatiblePlanner,
)
from operations_copilot.tools import default_registry


class FakeCompletions:
    def create(self, **kwargs):
        assert kwargs["model"] == "qwen2.5-coder:7b"
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=json.dumps(
                            {
                                "tool_name": "task_creator",
                                "arguments": {"title": "Review order"},
                            }
                        )
                    )
                )
            ]
        )


class FakeClient:
    chat = SimpleNamespace(completions=FakeCompletions())


def test_heuristic_planner_keeps_offline_tests_deterministic():
    plan = HeuristicPlanner().plan("گزارش سفارش‌ها", default_registry())
    assert plan.tool_name == "report_builder"


def test_compatible_planner_validates_selected_tool():
    settings = Settings(
        ai_provider="ollama",
        chat_model="qwen2.5-coder:7b",
    )
    planner = OpenAICompatiblePlanner(settings, client=FakeClient())
    plan = planner.plan("Review the order", default_registry())

    assert plan.tool_name == "task_creator"
    assert plan.arguments == {"title": "Review order"}


def test_planner_rejects_unknown_tool():
    class UnknownCompletions:
        def create(self, **kwargs):
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content='{"tool_name":"shell","arguments":{}}'
                        )
                    )
                ]
            )

    client = SimpleNamespace(chat=SimpleNamespace(completions=UnknownCompletions()))
    planner = OpenAICompatiblePlanner(
        Settings(ai_provider="ollama"),
        client=client,
    )
    with pytest.raises(ValueError, match="Unknown tool"):
        planner.plan("run shell", default_registry())
