import json
from dataclasses import dataclass
from typing import Protocol

from openai import OpenAI

from .config import Settings
from .tools import ToolRegistry


@dataclass(frozen=True)
class ToolPlan:
    tool_name: str
    arguments: dict


class Planner(Protocol):
    def plan(self, request: str, registry: ToolRegistry) -> ToolPlan: ...


class HeuristicPlanner:
    def plan(self, request: str, registry: ToolRegistry) -> ToolPlan:
        if "report" in request.lower() or "گزارش" in request:
            return ToolPlan("report_builder", {"topic": request})
        return ToolPlan("task_creator", {"title": request})


class OpenAICompatiblePlanner:
    def __init__(self, settings: Settings, client: OpenAI | None = None) -> None:
        api_key = settings.provider_api_key or settings.openai_api_key
        if settings.ai_provider == "ollama":
            api_key = api_key or "ollama"
        if not api_key:
            raise ValueError("A provider API key is required")
        base_url = settings.provider_base_url
        if settings.ai_provider == "ollama" and not base_url:
            base_url = "http://localhost:11434/v1"
        self.client = client or OpenAI(api_key=api_key, base_url=base_url)
        self.model = settings.chat_model

    def plan(self, request: str, registry: ToolRegistry) -> ToolPlan:
        manifest = registry.manifest()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Select exactly one tool. Return JSON only with keys "
                        "tool_name and arguments. Never invent a tool."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps({"request": request, "tools": manifest}),
                },
            ],
        )
        content = response.choices[0].message.content or "{}"
        payload = json.loads(content)
        tool_name = str(payload["tool_name"])
        registry.get(tool_name)
        arguments = payload.get("arguments", {})
        if not isinstance(arguments, dict):
            raise ValueError("Planner arguments must be an object")
        return ToolPlan(tool_name, arguments)


def build_planner(settings: Settings) -> Planner:
    if settings.ai_provider == "heuristic":
        return HeuristicPlanner()
    return OpenAICompatiblePlanner(settings)
