from uuid import uuid4

import pytest

from app.toolbus import ToolBus, ToolContext, ToolRequest, ToolResult


@pytest.mark.asyncio
async def test_dispatches_registered_capability() -> None:
    bus = ToolBus()

    async def handler(request: ToolRequest, context: ToolContext) -> ToolResult:
        return ToolResult(request.request_id, request.capability, True, output={"ok": True})

    bus.register("test.echo", handler)
    context = ToolContext(uuid4(), "/tmp/ctfos")
    result = await bus.dispatch(
        ToolRequest("test.echo"), context, allowed_capabilities={"test.echo": True}
    )

    assert result.ok is True
    assert result.output == {"ok": True}
    assert result.duration_ms >= 0


@pytest.mark.asyncio
async def test_denies_capability_by_policy() -> None:
    bus = ToolBus()

    async def handler(request: ToolRequest, context: ToolContext) -> ToolResult:
        raise AssertionError("denied handler must not execute")

    bus.register("test.echo", handler)
    result = await bus.dispatch(
        ToolRequest("test.echo"),
        ToolContext(uuid4(), "/tmp/ctfos"),
        allowed_capabilities={"test.echo": False},
    )

    assert result.ok is False
    assert result.error == "capability_denied"
