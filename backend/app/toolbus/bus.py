from __future__ import annotations

import time
from collections.abc import Mapping

from app.toolbus.models import ToolContext, ToolHandler, ToolRequest, ToolResult


class ToolBus:
    """Shared dispatch layer used by all specialists.

    The bus owns capability lookup and authorization checks; concrete tools remain
    isolated behind handlers. This keeps agents independent of tool implementations.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, ToolHandler] = {}

    def register(self, capability: str, handler: ToolHandler) -> None:
        if not capability or capability in self._handlers:
            raise ValueError(f"Invalid or duplicate capability: {capability}")
        self._handlers[capability] = handler

    def capabilities(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))

    async def dispatch(
        self,
        request: ToolRequest,
        context: ToolContext,
        *,
        allowed_capabilities: Mapping[str, bool] | None = None,
    ) -> ToolResult:
        if not context.authorized:
            return ToolResult(request.request_id, request.capability, False, error="unauthorized")
        if allowed_capabilities is not None and not allowed_capabilities.get(request.capability, False):
            return ToolResult(request.request_id, request.capability, False, error="capability_denied")

        handler = self._handlers.get(request.capability)
        if handler is None:
            return ToolResult(request.request_id, request.capability, False, error="capability_not_found")

        started = time.perf_counter()
        result = await handler(request, context)
        duration_ms = (time.perf_counter() - started) * 1000
        return ToolResult(
            request_id=result.request_id,
            capability=result.capability,
            ok=result.ok,
            output=result.output,
            error=result.error,
            started_at=result.started_at,
            duration_ms=duration_ms,
        )
