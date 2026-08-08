from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class Evidence:
    """Immutable observation produced by a tool, capability, or specialist."""

    kind: str
    value: str
    source: str
    confidence: float = 1.0
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.kind or not self.source:
            raise ValueError("kind and source are required")
