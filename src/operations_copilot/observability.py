from time import monotonic

from prometheus_client import Counter, Histogram

RUNS = Counter("copilot_agent_runs_total", "Agent runs by terminal status", ["status"])
RUN_DURATION = Histogram("copilot_agent_run_duration_seconds", "Agent run duration")
TOOL_CALLS = Counter("copilot_tool_calls_total", "Tool calls by tool and outcome", ["tool", "outcome"])
TOOL_RETRIES = Counter("copilot_tool_retries_total", "Retried tool calls", ["tool"])


class RunTimer:
    def __init__(self) -> None:
        self.started_at = monotonic()

    def observe(self, status: str) -> None:
        RUN_DURATION.observe(monotonic() - self.started_at)
        RUNS.labels(status=status).inc()
