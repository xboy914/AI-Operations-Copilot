from operations_copilot.agent import AgentRuntime


def test_safe_request_completes_end_to_end_without_approval():
    runtime = AgentRuntime()
    result = runtime.start("Build the weekly operations report", "e2e-safe")
    assert result["status"] == "completed"
    assert result["result"]["type"] == "report"
    assert runtime.events.get_run("e2e-safe")["status"] == "completed"


def test_risky_request_requires_a_human_and_records_the_decision():
    runtime = AgentRuntime()
    pending = runtime.start("Follow up with the supplier", "e2e-risky", actor="operator@test")
    assert pending["status"] == "waiting_approval"
    assert pending["approval"]["tool"] == "task_creator"

    completed = runtime.resume("e2e-risky", True, actor="approver@test")
    assert completed["status"] == "completed"
    projection = runtime.events.get_run("e2e-risky")
    assert projection["decided_by"] == "approver@test"
    assert projection["result"]["created"] is True


def test_rejected_request_never_executes_the_side_effect():
    runtime = AgentRuntime()
    runtime.start("Escalate delayed shipment", "e2e-reject")
    result = runtime.resume("e2e-reject", False, actor="approver@test")
    assert result["status"] == "rejected"
    assert result["result"] == {"executed": False}
