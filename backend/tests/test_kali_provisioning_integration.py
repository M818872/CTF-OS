import pytest

from app.runtime.command_runner import CommandResult
from app.runtime.kali_executor import KaliToolExecutor


class FakeRunner:
    async def run(self, command: str) -> CommandResult:
        return CommandResult(command, 0, "CTF{provisioned}", "", False)


class FakeProvisioner:
    def __init__(self) -> None:
        self.checked = False
        self.install_command: str | None = None

    def installed(self, _tool) -> bool:
        return self.checked

    async def ensure(self, _tool_name: str, custom_command: str | None = None) -> bool:
        self.install_command = custom_command
        self.checked = True
        return True


@pytest.mark.asyncio
async def test_missing_tool_is_provisioned_then_executed() -> None:
    provisioner = FakeProvisioner()
    result = await KaliToolExecutor(FakeRunner(), provisioner).run(
        "nmap", ["-sV"], custom_install_command="custom-installer nmap"
    )
    assert result.tokens == ("CTF{provisioned}",)
    assert provisioner.install_command == "custom-installer nmap"
