from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    requires_approval: bool
    handler: Callable[[dict[str, Any]], dict[str, Any]]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, tool: ToolSpec) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolSpec:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ValueError(f"Unknown tool: {name}") from exc

    def manifest(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "requires_approval": tool.requires_approval,
            }
            for tool in sorted(self._tools.values(), key=lambda item: item.name)
        ]


def build_report(arguments: dict[str, Any]) -> dict[str, Any]:
    topic = str(arguments.get("topic", "operations"))
    return {"type": "report", "title": f"{topic.title()} summary", "rows": 0}


def create_task(arguments: dict[str, Any]) -> dict[str, Any]:
    title = str(arguments.get("title", "")).strip()
    if not title:
        raise ValueError("Task title is required")
    return {"type": "task", "title": title, "created": True}


def default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name="report_builder",
            description="Build a read-only operational report.",
            requires_approval=False,
            handler=build_report,
        )
    )
    registry.register(
        ToolSpec(
            name="task_creator",
            description="Create a follow-up task with an external side effect.",
            requires_approval=True,
            handler=create_task,
        )
    )
    return registry
