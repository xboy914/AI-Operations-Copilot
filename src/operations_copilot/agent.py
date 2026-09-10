from typing import Any, TypedDict
from uuid import uuid4

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .planner import HeuristicPlanner, Planner
from .tools import ToolRegistry, default_registry


class AgentState(TypedDict, total=False):
    request: str
    tool_name: str
    arguments: dict[str, Any]
    approved: bool
    status: str
    result: dict[str, Any]


def legacy_plan(state: AgentState) -> AgentState:
    request = state["request"]
    lowered = request.lower()
    if "report" in lowered or "گزارش" in request:
        return {
            "tool_name": "report_builder",
            "arguments": {"topic": request},
            "status": "planned",
        }
    return {
        "tool_name": "task_creator",
        "arguments": {"title": request},
        "status": "planned",
    }


class AgentRuntime:
    def __init__(
        self,
        registry: ToolRegistry | None = None,
        planner: Planner | None = None,
    ) -> None:
        self.registry = registry or default_registry()
        self.planner = planner or HeuristicPlanner()
        builder = StateGraph(AgentState)
        builder.add_node("plan", self._plan)
        builder.add_node("approval", self._approval)
        builder.add_node("execute", self._execute)
        builder.add_edge(START, "plan")
        builder.add_edge("plan", "approval")
        builder.add_edge("approval", "execute")
        builder.add_edge("execute", END)
        self.graph = builder.compile(checkpointer=InMemorySaver())

    def _plan(self, state: AgentState) -> AgentState:
        plan = self.planner.plan(state["request"], self.registry)
        return {
            "tool_name": plan.tool_name,
            "arguments": plan.arguments,
            "status": "planned",
        }

    def _approval(self, state: AgentState) -> AgentState:
        tool = self.registry.get(state["tool_name"])
        if not tool.requires_approval:
            return {"approved": True, "status": "approved_automatically"}
        decision = interrupt(
            {
                "kind": "tool_approval",
                "tool": tool.name,
                "description": tool.description,
                "arguments": state["arguments"],
            }
        )
        return {
            "approved": bool(decision.get("approved", False)),
            "status": "approved" if decision.get("approved") else "rejected",
        }

    def _execute(self, state: AgentState) -> AgentState:
        if not state.get("approved"):
            return {"status": "rejected", "result": {"executed": False}}
        tool = self.registry.get(state["tool_name"])
        return {"status": "completed", "result": tool.handler(state["arguments"])}

    def start(self, request: str, thread_id: str | None = None) -> dict[str, Any]:
        run_id = thread_id or str(uuid4())
        config = {"configurable": {"thread_id": run_id}}
        output = self.graph.invoke({"request": request}, config=config)
        return self._result(run_id, output)

    def resume(self, thread_id: str, approved: bool) -> dict[str, Any]:
        config = {"configurable": {"thread_id": thread_id}}
        output = self.graph.invoke(
            Command(resume={"approved": approved}),
            config=config,
        )
        return self._result(thread_id, output)

    @staticmethod
    def _result(thread_id: str, output: dict[str, Any]) -> dict[str, Any]:
        interruptions = output.get("__interrupt__", ())
        return {
            "thread_id": thread_id,
            "status": "waiting_approval" if interruptions else output.get("status"),
            "tool_name": output.get("tool_name"),
            "result": output.get("result"),
            "approval": interruptions[0].value if interruptions else None,
        }


runtime = AgentRuntime()
