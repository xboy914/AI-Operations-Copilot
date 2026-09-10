import pytest

from operations_copilot.resilience import RetryPolicy, RetryableToolError, execute_with_retry


def test_transient_failure_is_retried_with_backoff():
    attempts = 0
    delays = []

    def flaky():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RetryableToolError("timeout")
        return {"ok": True}

    result = execute_with_retry(
        "crm.read",
        flaky,
        RetryPolicy(max_attempts=3, initial_delay_seconds=0.1),
        sleeper=delays.append,
    )
    assert result == {"ok": True}
    assert attempts == 3
    assert delays == [0.1, 0.2]


def test_permanent_errors_are_never_retried():
    attempts = 0

    def invalid():
        nonlocal attempts
        attempts += 1
        raise ValueError("invalid input")

    with pytest.raises(ValueError):
        execute_with_retry("crm.write", invalid, RetryPolicy(), sleeper=lambda _: None)
    assert attempts == 1


def test_retry_budget_is_bounded():
    with pytest.raises(RetryableToolError):
        execute_with_retry(
            "crm.read",
            lambda: (_ for _ in ()).throw(RetryableToolError("offline")),
            RetryPolicy(max_attempts=2),
            sleeper=lambda _: None,
        )
