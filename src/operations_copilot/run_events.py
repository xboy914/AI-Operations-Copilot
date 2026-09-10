from copy import deepcopy
from datetime import UTC, datetime
from threading import RLock
from typing import Any


class RunEventStore:
    """Thread-safe live projection; replaceable with Redis Streams."""

    def __init__(self) -> None:
        self._runs: dict[str, dict[str, Any]] = {}
        self._events: dict[str, list[dict[str, Any]]] = {}
        self._lock = RLock()

    def publish(self, thread_id: str, event_type: str, snapshot: dict[str, Any]) -> dict:
        with self._lock:
            events = self._events.setdefault(thread_id, [])
            event = {
                "sequence": len(events) + 1,
                "type": event_type,
                "thread_id": thread_id,
                "status": snapshot["status"],
                "timestamp": datetime.now(UTC).isoformat(),
                "data": deepcopy(snapshot),
            }
            events.append(event)
            self._runs[thread_id] = deepcopy(snapshot) | {
                "thread_id": thread_id,
                "updated_at": event["timestamp"],
                "sequence": event["sequence"],
            }
            return deepcopy(event)

    def get_run(self, thread_id: str) -> dict:
        with self._lock:
            if thread_id not in self._runs:
                raise KeyError(thread_id)
            return deepcopy(self._runs[thread_id])

    def list_runs(self, status: str | None = None) -> list[dict]:
        with self._lock:
            runs = [deepcopy(run) for run in self._runs.values()]
        if status is not None:
            runs = [run for run in runs if run["status"] == status]
        return sorted(runs, key=lambda run: run["updated_at"], reverse=True)

    def events_after(self, thread_id: str, sequence: int = 0) -> list[dict]:
        with self._lock:
            if thread_id not in self._events:
                raise KeyError(thread_id)
            return deepcopy(self._events[thread_id][sequence:])
