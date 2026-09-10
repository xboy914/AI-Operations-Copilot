from collections.abc import Callable
from dataclasses import dataclass
from time import sleep
from typing import Any

from .observability import TOOL_CALLS, TOOL_RETRIES


class RetryableToolError(RuntimeError):
    """A transient integration failure that is safe to retry."""


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    initial_delay_seconds: float = 0.05
    backoff_multiplier: float = 2.0


def execute_with_retry(
    tool_name: str,
    operation: Callable[[], dict[str, Any]],
    policy: RetryPolicy,
    sleeper: Callable[[float], None] = sleep,
) -> dict[str, Any]:
    delay = policy.initial_delay_seconds
    for attempt in range(1, policy.max_attempts + 1):
        try:
            result = operation()
            TOOL_CALLS.labels(tool=tool_name, outcome="success").inc()
            return result
        except RetryableToolError:
            if attempt == policy.max_attempts:
                TOOL_CALLS.labels(tool=tool_name, outcome="failed").inc()
                raise
            TOOL_RETRIES.labels(tool=tool_name).inc()
            sleeper(delay)
            delay *= policy.backoff_multiplier
    raise RuntimeError("Retry loop exhausted")
