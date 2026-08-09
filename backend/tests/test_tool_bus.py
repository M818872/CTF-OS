import pytest

from app.services.execution import CapabilityExecutionService
from app.specialists.agents import get_agent
from app.tools.bus import ToolBus
from app.tools.registry import get_tool, list_tools


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


def test_specialist_capabilities_are_discoverable() -> None:
    names = {tool.name for tool in list_tools()}
    assert "crypto.analyze" in names
    assert "web.analyze" in names
    assert "forensics.analyze" in names
    assert "reverse.analyze" in names
    assert "network.analyze" in names
    assert "stego.analyze" in names
    assert "osint.analyze" in names
    assert "mobile.analyze" in names
    assert "blockchain.analyze" in names
    assert "terminal.execute" in names


@pytest.mark.asyncio
async def test_terminal_capability_uses_runtime_runner(monkeypatch: pytest.MonkeyPatch) -> None:
    service = CapabilityExecutionService()

    async def fake_terminal(command: str):
        return type(
            "Result",
            (),
            {
                "command": command,
                "returncode": 0,
                "stdout": "CTF{runtime_test}",
                "stderr": "",
                "timed_out": False,
                "tokens": ["CTF{runtime_test}"],
            },
        )()

    monkeypatch.setattr(service, "execute_terminal", fake_terminal)
    result = await service.execute_async("terminal.execute", "printf test")

    assert result.result.status == "success"
    assert result.result.data["tokens"] == ["CTF{runtime_test}"]
    assert get_tool("terminal.execute") is not None
