from operations_copilot.agent import AgentRuntime


def test_read_only_report_runs_without_human_approval():
    result = AgentRuntime().start("Build an operations report", thread_id="report-1")

    assert result["status"] == "completed"
    assert result["tool_name"] == "report_builder"
    assert result["approval"] is None


def test_side_effect_tool_pauses_and_resumes_after_approval():
    runtime = AgentRuntime()
    pending = runtime.start("Follow up with the supplier", thread_id="task-1")

    assert pending["status"] == "waiting_approval"
    assert pending["approval"]["tool"] == "task_creator"

    completed = runtime.resume("task-1", approved=True)
    assert completed["status"] == "completed"
    assert completed["result"]["created"] is True


def test_rejection_prevents_tool_execution():
    runtime = AgentRuntime()
    runtime.start("Escalate the delayed order", thread_id="task-2")

    rejected = runtime.resume("task-2", approved=False)
    assert rejected == {
        "thread_id": "task-2",
        "status": "rejected",
        "tool_name": "task_creator",
        "result": {"executed": False},
        "approval": None,
    }
