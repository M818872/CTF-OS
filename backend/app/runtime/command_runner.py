from __future__ import annotations

import asyncio
import os
import shlex
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommandResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool


class CommandRunner:
    """Run commands exposed to a CTF-OS investigation workspace.

    The runner is intentionally environment-configurable. In a dedicated CTF
    container, CTF_OS_EXECUTION_MODE=direct permits the agent to use the
    container's installed tooling. The default mode is disabled so an
    accidentally deployed API cannot become a remote command endpoint.
    """

    def __init__(self, timeout: int | None = None) -> None:
        self.timeout = timeout or int(os.getenv("CTF_OS_COMMAND_TIMEOUT", "120"))
        self.mode = os.getenv("CTF_OS_EXECUTION_MODE", "disabled")

    async def run(self, command: str) -> CommandResult:
        command = command.strip()
        if not command:
            raise ValueError("command is required")
        if self.mode != "direct":
            raise RuntimeError("terminal execution is disabled; set CTF_OS_EXECUTION_MODE=direct in the CTF runtime")

        # shlex keeps the command as argv instead of handing it to a shell.
        argv = shlex.split(command)
        process = await asyncio.create_subprocess_exec(
            *argv,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=os.environ.copy(),
        )
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.timeout)
            return CommandResult(command, process.returncode or 0, stdout.decode(errors="replace"), stderr.decode(errors="replace"), False)
        except TimeoutError:
            process.kill()
            await process.communicate()
            return CommandResult(command, -1, "", f"command timed out after {self.timeout}s", True)
