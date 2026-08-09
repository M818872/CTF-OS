from __future__ import annotations

import os
import shlex
import shutil

from app.runtime.command_runner import CommandRunner
from app.runtime.kali_catalog import KaliTool, get_kali_tool

_DEFAULT_PACKAGES: dict[str, str] = {
    "nmap": "nmap",
    "masscan": "masscan",
    "curl": "curl",
    "wget": "wget",
    "gobuster": "gobuster",
    "ffuf": "ffuf",
    "nikto": "nikto",
    "sqlmap": "sqlmap",
    "dig": "dnsutils",
    "whois": "whois",
    "tcpdump": "tcpdump",
    "tshark": "tshark",
    "wireshark": "wireshark",
    "file": "file",
    "strings": "binutils",
    "xxd": "xxd",
    "binwalk": "binwalk",
    "exiftool": "libimage-exiftool-perl",
    "dd": "coreutils",
    "readelf": "binutils",
    "objdump": "binutils",
    "nm": "binutils",
    "gdb": "gdb",
    "radare2": "radare2",
    "checksec": "checksec",
    "ROPgadget": "ropgadget",
    "openssl": "openssl",
    "python3": "python3",
    "git": "git",
    "steghide": "steghide",
    "stegseek": "stegseek",
    "zsteg": "zsteg",
    "apktool": "apktool",
    "jadx": "jadx",
    "adb": "adb",
}


class ToolProvisioner:
    """Detect and optionally install missing CTF runtime tools."""

    def __init__(self, runner: CommandRunner | None = None) -> None:
        self.runner = runner or CommandRunner()
        self.auto_install = os.getenv("CTF_OS_AUTO_INSTALL", "0") == "1"

    @staticmethod
    def installed(tool: KaliTool) -> bool:
        return shutil.which(tool.binary) is not None

    async def ensure(
        self,
        tool_name: str,
        custom_command: str | None = None,
    ) -> bool:
        tool = get_kali_tool(tool_name)
        if tool is None:
            raise ValueError(f"unknown Kali tool: {tool_name}")
        if self.installed(tool):
            return True
        if not self.auto_install:
            return False

        command = custom_command or self._apt_command(tool)
        if command is None:
            raise RuntimeError(
                f"tool {tool_name!r} is missing and has no known installer; "
                "provide a custom install command"
            )
        result = await self.runner.run(command)
        if result.returncode != 0 or result.timed_out:
            raise RuntimeError(
                f"failed to install {tool_name!r}: {result.stderr.strip() or result.stdout.strip()}"
            )
        return self.installed(tool)

    @staticmethod
    def _apt_command(tool: KaliTool) -> str | None:
        package = _DEFAULT_PACKAGES.get(tool.name)
        if package is None or shutil.which("apt-get") is None:
            return None
        return f"apt-get install -y {shlex.quote(package)}"
