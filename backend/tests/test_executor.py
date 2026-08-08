import pytest

from app.execution.local import ExecutionPolicy, LocalExecutor
from app.execution.models import ExecutionRequest


@pytest.mark.asyncio
async def test_allowed_command_executes() -> None:
    executor = LocalExecutor(ExecutionPolicy(frozenset({"python"})))
    result = await executor.execute(
        ExecutionRequest(("python", "-c", "print('ctf-os')"))
    )
    assert result.status == "success"
    assert result.stdout.strip() == "ctf-os"


@pytest.mark.asyncio
async def test_disallowed_command_is_rejected() -> None:
    executor = LocalExecutor(ExecutionPolicy(frozenset({"python"})))
    with pytest.raises(PermissionError):
        await executor.execute(ExecutionRequest(("sh", "-c", "echo no")))
