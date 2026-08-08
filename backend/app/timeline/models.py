from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class TimelineEvent:
    event_type: str
    message: str
    source: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class Timeline:
    def __init__(self) -> None:
        self._events: dict[UUID, list[TimelineEvent]] = {}

    def append(self, investigation_id: UUID, event: TimelineEvent) -> TimelineEvent:
        self._events.setdefault(investigation_id, []).append(event)
        return event

    def list(self, investigation_id: UUID) -> tuple[TimelineEvent, ...]:
        return tuple(self._events.get(investigation_id, ()))
