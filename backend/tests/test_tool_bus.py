import pytest

from app.specialists.agents import get_agent
from app.tools.bus import ToolBus


def test_tool_bus_routes_registered_capability() -> None:
    bus = ToolBus()
    route = bus.route("crypto.decode")
    assert route.specialist == "crypto"
    assert route.capability == "crypto.decode"


def test_tool_bus_executes_through_registered_service() -> None:
    bus = ToolBus()
    result = bus.execute("crypto.decode", "48656c6c6f")
    assert result.capability == "crypto.decode"
    assert result.result.data["candidates"]["hex"] == "Hello"


def test_tool_bus_rejects_unknown_capability() -> None:
    with pytest.raises(ValueError, match="Unknown capability"):
        ToolBus().route("not-a-capability")


def test_tool_bus_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="input_text"):
        ToolBus().execute("crypto.decode", " ")


def test_specialist_agent_uses_shared_bus() -> None:
    bus = ToolBus()
    agent = get_agent("crypto", bus)
    assert agent is not None
    result = agent.execute(agent.plan("48656c6c6f", "crypto.decode"))
    assert result.specialist == "crypto"
    assert result.result.data["candidates"]["hex"] == "Hello"
