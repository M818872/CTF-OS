from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class Evidence:
    kind: str
    value: str
    source: str
    confidence: float = 1.0
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TimelineEvent:
    action: str
    status: str
    source: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


class EvidenceStore:
    def __init__(self) -> None:
        self._evidence: dict[UUID, list[Evidence]] = {}
        self._timeline: dict[UUID, list[TimelineEvent]] = {}

    def add_evidence(self, investigation_id: UUID, evidence: Evidence) -> Evidence:
        self._evidence.setdefault(investigation_id, []).append(evidence)
        return evidence

    def add_event(self, investigation_id: UUID, event: TimelineEvent) -> TimelineEvent:
        self._timeline.setdefault(investigation_id, []).append(event)
        return event

    def evidence(self, investigation_id: UUID) -> tuple[Evidence, ...]:
        return tuple(self._evidence.get(investigation_id, ()))

    def timeline(self, investigation_id: UUID) -> tuple[TimelineEvent, ...]:
        return tuple(self._timeline.get(investigation_id, ()))
