import pytest

from app.runtime.command_runner import CommandResult
from app.runtime.kali_executor import KaliToolExecutor
from app.tools.bus import ToolBus


class FakeRunner:
    async def run(self, command: str) -> CommandResult:
        return CommandResult(command, 0, "10.0.0.8 CTF{bus_runtime}", "", False)


@pytest.mark.asyncio
async def test_tool_bus_executes_kali_tool_through_runtime() -> None:
    bus = ToolBus(kali=KaliToolExecutor(FakeRunner()))
    result = await bus.execute_kali("nmap", ["10.0.0.8"])
    assert result.tool == "nmap"
    assert result.returncode == 0
    assert "CTF{bus_runtime}" in result.tokens
    assert "10.0.0.8" in result.findings


@pytest.mark.asyncio
async def test_tool_bus_rejects_unknown_kali_tool() -> None:
    bus = ToolBus(kali=KaliToolExecutor(FakeRunner()))
    with pytest.raises(ValueError, match="unknown Kali tool"):
        await bus.execute_kali("not-a-kali-tool", [])
