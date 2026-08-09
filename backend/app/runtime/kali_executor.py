from __future__ import annotations

import re
import shlex
from dataclasses import dataclass

from app.runtime.command_runner import CommandRunner
from app.runtime.kali_catalog import KaliTool, get_kali_tool
from app.runtime.result_parser import extract_tokens


_IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_URL = re.compile(r"https?://[^\s\"'<>]+")
_HEX_HASH = re.compile(r"\b[a-fA-F0-9]{32,128}\b")


@dataclass(frozen=True, slots=True)
class KaliExecutionResult:
    tool: str
    category: str
    command: str
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    tokens: tuple[str, ...]
    findings: tuple[str, ...]


class KaliToolExecutor:
    """Run cataloged Kali tools through the CTF runtime command boundary."""

    def __init__(self, runner: CommandRunner | None = None) -> None:
        self.runner = runner or CommandRunner()

    async def run(self, tool_name: str, args: list[str]) -> KaliExecutionResult:
        tool = get_kali_tool(tool_name)
        if tool is None:
            raise ValueError(f"unknown Kali tool: {tool_name}")
        if any(not isinstance(arg, str) for arg in args):
            raise TypeError("tool arguments must be strings")
        command = shlex.join([tool.binary, *args])
        result = await self.runner.run(command)
        combined = f"{result.stdout}\n{result.stderr}"
        return KaliExecutionResult(
            tool=tool.name,
            category=tool.category,
            command=result.command,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            timed_out=result.timed_out,
            tokens=tuple(extract_tokens(combined)),
            findings=self._findings(combined),
        )

    @staticmethod
    def _findings(text: str) -> tuple[str, ...]:
        values: list[str] = []
        for pattern in (_IP, _URL, _HEX_HASH):
            for value in pattern.findall(text):
                if value not in values:
                    values.append(value)
        return tuple(values)

    @staticmethod
    def describe(tool_name: str) -> KaliTool:
        tool = get_kali_tool(tool_name)
        if tool is None:
            raise ValueError(f"unknown Kali tool: {tool_name}")
        return tool
