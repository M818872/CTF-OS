from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ToolContext:
    investigation_id: UUID
    workspace: str
    authorized: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ToolRequest:
    capability: str
    arguments: dict[str, Any] = field(default_factory=dict)
    timeout_seconds: float = 30.0
    request_id: UUID = field(default_factory=uuid4)


@dataclass(frozen=True, slots=True)
class ToolResult:
    request_id: UUID
    capability: str
    ok: bool
    output: Any = None
    error: str | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: float = 0.0


class ToolHandler(Protocol):
    async def __call__(self, request: ToolRequest, context: ToolContext) -> ToolResult: ...
