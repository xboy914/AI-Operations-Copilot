from operations_copilot.agent import AgentRuntime
from operations_copilot.run_events import RunEventStore


def test_store_projects_pending_approval():
    store = RunEventStore()
    store.publish("one", "run.started", {"status": "running", "request": "one"})
    store.publish("one", "approval.requested",
                  {"status": "waiting_approval", "request": "one"})
    assert store.list_runs("waiting_approval")[0]["thread_id"] == "one"
    assert [event["sequence"] for event in store.events_after("one")] == [1, 2]


def test_runtime_publishes_full_approval_lifecycle():
    runtime = AgentRuntime()
    runtime.start("Follow up with supplier", thread_id="task-live")
    assert runtime.events.get_run("task-live")["status"] == "waiting_approval"
    runtime.resume("task-live", True, actor="approver@example.com")
    assert [event["type"] for event in runtime.events.events_after("task-live")] == [
        "run.started", "approval.requested", "approval.decided", "run.completed"]
