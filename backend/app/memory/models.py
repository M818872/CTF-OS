from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class MemoryItem:
    kind: str
    content: Any
    source: str
    confidence: float = 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class SharedMemory:
    """In-process memory contract; persistent storage can implement the same API."""

    def __init__(self) -> None:
        self._items: list[MemoryItem] = []

    def remember(self, item: MemoryItem) -> None:
        self._items.append(item)

    def all(self) -> tuple[MemoryItem, ...]:
        return tuple(self._items)

    def by_kind(self, kind: str) -> tuple[MemoryItem, ...]:
        return tuple(item for item in self._items if item.kind == kind)
