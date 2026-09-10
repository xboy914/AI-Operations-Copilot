from typing import Any, TypedDict
from uuid import uuid4

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .config import get_settings
from .planner import Planner, build_planner
from .run_events import RunEventStore
from .tools import ToolRegistry, default_registry


class AgentState(TypedDict, total=False):
    request: str
    tool_name: str
    arguments: dict[str, Any]
    approved: bool
    status: str
    result: dict[str, Any]


class AgentRuntime:
    def __init__(self, registry: ToolRegistry | None = None,
                 planner: Planner | None = None, events: RunEventStore | None = None) -> None:
        self.registry = registry or default_registry()
        self.planner = planner or build_planner(get_settings())
        self.events = events or RunEventStore()
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
        return {"tool_name": plan.tool_name, "arguments": plan.arguments, "status": "planned"}

    def _approval(self, state: AgentState) -> AgentState:
        tool = self.registry.get(state["tool_name"])
        if not tool.requires_approval:
            return {"approved": True, "status": "approved_automatically"}
        decision = interrupt({"kind": "tool_approval", "tool": tool.name,
            "description": tool.description, "arguments": state["arguments"]})
        approved = bool(decision.get("approved", False))
        return {"approved": approved, "status": "approved" if approved else "rejected"}

    def _execute(self, state: AgentState) -> AgentState:
        if not state.get("approved"):
            return {"status": "rejected", "result": {"executed": False}}
        tool = self.registry.get(state["tool_name"])
        return {"status": "completed", "result": tool.handler(state["arguments"])}

    def start(self, request: str, thread_id: str | None = None,
              actor: str = "system") -> dict[str, Any]:
        run_id = thread_id or str(uuid4())
        self.events.publish(run_id, "run.started",
                            {"status": "running", "request": request, "actor": actor})
        config = {"configurable": {"thread_id": run_id}}
        try:
            result = self._result(run_id, self.graph.invoke({"request": request}, config=config))
            snapshot = result | {"request": request, "actor": actor}
            event_type = "approval.requested" if result["approval"] else "run.completed"
            self.events.publish(run_id, event_type, snapshot)
            return result
        except Exception:
            self.events.publish(run_id, "run.failed",
                                {"status": "failed", "request": request, "actor": actor})
            raise

    def resume(self, thread_id: str, approved: bool,
               actor: str = "system") -> dict[str, Any]:
        previous = self.events.get_run(thread_id)
        if previous["status"] != "waiting_approval":
            raise ValueError("Run is not waiting for approval")
        self.events.publish(thread_id, "approval.decided", previous | {
            "status": "approved" if approved else "rejected",
            "decision": approved, "decided_by": actor,
        })
        config = {"configurable": {"thread_id": thread_id}}
        output = self.graph.invoke(Command(resume={"approved": approved}), config=config)
        result = self._result(thread_id, output)
        snapshot = result | {
            "request": previous["request"], "actor": previous["actor"], "decided_by": actor}
        self.events.publish(thread_id, "run.completed" if approved else "run.rejected", snapshot)
        return result

    @staticmethod
    def _result(thread_id: str, output: dict[str, Any]) -> dict[str, Any]:
        interruptions = output.get("__interrupt__", ())
        return {"thread_id": thread_id,
                "status": "waiting_approval" if interruptions else output.get("status"),
                "tool_name": output.get("tool_name"), "result": output.get("result"),
                "approval": interruptions[0].value if interruptions else None}


runtime = AgentRuntime()
