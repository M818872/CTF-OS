import pytest

from app.runtime.command_runner import CommandResult
from app.runtime.kali_executor import KaliToolExecutor


class FakeRunner:
    async def run(self, command: str) -> CommandResult:
        return CommandResult(
            command=command,
            returncode=0,
            stdout="host 10.10.10.5 https://example.test CTF{runtime_ok} 0123456789abcdef0123456789abcdef",
            stderr="",
            timed_out=False,
        )


class InstalledProvisioner:
    @staticmethod
    def installed(_tool) -> bool:
        return True


@pytest.mark.asyncio
async def test_kali_executor_runs_catalog_tool_and_extracts_findings() -> None:
    result = await KaliToolExecutor(FakeRunner(), InstalledProvisioner()).run("nmap", ["-sV", "10.10.10.5"])
    assert result.tool == "nmap"
    assert result.category == "network"
    assert result.returncode == 0
    assert "nmap -sV 10.10.10.5" == result.command
    assert "CTF{runtime_ok}" in result.tokens
    assert "10.10.10.5" in result.findings
    assert "https://example.test" in result.findings


@pytest.mark.asyncio
async def test_kali_executor_quotes_arguments_without_shell_interpretation() -> None:
    result = await KaliToolExecutor(FakeRunner(), InstalledProvisioner()).run("curl", ["https://example.test/a b"])
    assert result.command == "curl 'https://example.test/a b'"


@pytest.mark.asyncio
async def test_kali_executor_rejects_unknown_tool() -> None:
    with pytest.raises(ValueError, match="unknown Kali tool"):
        await KaliToolExecutor(FakeRunner(), InstalledProvisioner()).run("not-a-kali-tool", [])
