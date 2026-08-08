from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class MemoryEvent:
    investigation_id: UUID | None
    event_type: str
    capability: str
    input_text: str
    status: str
    summary: str
    data: dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class InvestigationMemory:
    """Append-only runtime memory for orchestration traces.

    A database-backed implementation can replace this class without changing
    the planner/orchestrator protocol.
    """

    def __init__(self) -> None:
        self._events: list[MemoryEvent] = []
        self._lock = Lock()

    def append(self, event: MemoryEvent) -> None:
        with self._lock:
            self._events.append(event)

    def events(self, investigation_id: UUID | None = None) -> tuple[MemoryEvent, ...]:
        with self._lock:
            if investigation_id is None:
                return tuple(self._events)
            return tuple(event for event in self._events if event.investigation_id == investigation_id)
