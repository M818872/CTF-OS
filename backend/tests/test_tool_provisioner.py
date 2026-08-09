from __future__ import annotations

import pytest

from app.runtime.command_runner import CommandResult
from app.runtime.kali_catalog import get_kali_tool
from app.runtime.tool_provisioner import ToolProvisioner


class FakeRunner:
    def __init__(self, returncode: int = 0) -> None:
        self.returncode = returncode
        self.commands: list[str] = []

    async def run(self, command: str) -> CommandResult:
        self.commands.append(command)
        return CommandResult(command, self.returncode, "installed", "", False)


def test_installed_uses_path_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    tool = get_kali_tool("nmap")
    assert tool is not None
    monkeypatch.setattr(
        "app.runtime.tool_provisioner.shutil.which",
        lambda _: "/usr/bin/nmap",
    )
    assert ToolProvisioner().installed(tool)


@pytest.mark.asyncio
async def test_custom_install_command_is_used_when_auto_install_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = FakeRunner()
    monkeypatch.setenv("CTF_OS_AUTO_INSTALL", "1")
    provisioner = ToolProvisioner(runner)
    tool = get_kali_tool("nmap")
    assert tool is not None
    states = iter((False, True))
    monkeypatch.setattr(provisioner, "installed", lambda _: next(states))
    monkeypatch.setattr(provisioner, "_apt_command", lambda _: None)
    assert await provisioner.ensure(tool.name, "custom-installer nmap")
    assert runner.commands == ["custom-installer nmap"]


@pytest.mark.asyncio
async def test_known_tool_uses_apt_package(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = FakeRunner()
    monkeypatch.setenv("CTF_OS_AUTO_INSTALL", "1")
    monkeypatch.setattr(
        "app.runtime.tool_provisioner.shutil.which",
        lambda name: "/usr/bin/apt-get" if name == "apt-get" else None,
    )
    provisioner = ToolProvisioner(runner)
    tool = get_kali_tool("nmap")
    assert tool is not None
    states = iter((False, True))
    monkeypatch.setattr(provisioner, "installed", lambda _: next(states))
    assert await provisioner.ensure(tool.name)
    assert runner.commands == ["apt-get install -y nmap"]


@pytest.mark.asyncio
async def test_failed_install_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = FakeRunner(returncode=1)
    monkeypatch.setenv("CTF_OS_AUTO_INSTALL", "1")
    provisioner = ToolProvisioner(runner)
    tool = get_kali_tool("nmap")
    assert tool is not None
    monkeypatch.setattr(provisioner, "installed", lambda _: False)
    monkeypatch.setattr(provisioner, "_apt_command", lambda _: "apt-get install -y nmap")
    with pytest.raises(RuntimeError, match="failed to install"):
        await provisioner.ensure(tool.name)


def test_missing_tool_is_not_installed_without_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CTF_OS_AUTO_INSTALL", raising=False)
    provisioner = ToolProvisioner()
    tool = get_kali_tool("nmap")
    assert tool is not None
    monkeypatch.setattr(provisioner, "installed", lambda _: False)
    assert provisioner.auto_install is False
