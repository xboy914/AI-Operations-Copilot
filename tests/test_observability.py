from prometheus_client import generate_latest

from operations_copilot.agent import AgentRuntime


def test_completed_run_is_exported_as_prometheus_metric():
    AgentRuntime().start("Build operations report", thread_id="metrics-test")
    metrics = generate_latest().decode()
    assert "copilot_agent_runs_total" in metrics
    assert 'status="completed"' in metrics
    assert "copilot_tool_calls_total" in metrics
