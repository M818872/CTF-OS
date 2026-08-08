from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from app.evidence.models import Evidence


class EvidenceStore:
    """Small interface-backed store; persistence can be swapped in later."""

    def __init__(self) -> None:
        self._items: dict[UUID, list[Evidence]] = defaultdict(list)

    def add(self, investigation_id: UUID, evidence: Evidence) -> Evidence:
        self._items[investigation_id].append(evidence)
        return evidence

    def list(self, investigation_id: UUID) -> tuple[Evidence, ...]:
        return tuple(self._items.get(investigation_id, ()))
