import pytest

from app.runtime.command_runner import CommandRunner


@pytest.mark.asyncio
async def test_terminal_runtime_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("CTF_OS_EXECUTION_MODE", raising=False)
    runner = CommandRunner()
    with pytest.raises(RuntimeError, match="terminal execution is disabled"):
        await runner.run("printf hello")


@pytest.mark.asyncio
async def test_direct_runtime_executes_argv_without_shell(monkeypatch) -> None:
    monkeypatch.setenv("CTF_OS_EXECUTION_MODE", "direct")
    runner = CommandRunner(timeout=5)
    result = await runner.run("printf hello")
    assert result.returncode == 0
    assert result.stdout == "hello"
    assert not result.timed_out
