from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path

from app.execution.models import ExecutionRequest, ExecutionResult


class ExecutionPolicy:
    def __init__(self, allowed_commands: frozenset[str], max_timeout_seconds: float = 30.0) -> None:
        self.allowed_commands = allowed_commands
        self.max_timeout_seconds = max_timeout_seconds

    def validate(self, request: ExecutionRequest) -> None:
        if not request.argv or not request.argv[0]:
            raise ValueError("argv must contain a command")
        command = Path(request.argv[0]).name
        if command not in self.allowed_commands:
            raise PermissionError(f"Command is not allowed: {command}")
        if request.timeout_seconds <= 0 or request.timeout_seconds > self.max_timeout_seconds:
            raise ValueError("timeout_seconds is outside the execution policy")


class LocalExecutor:
    def __init__(self, policy: ExecutionPolicy) -> None:
        self.policy = policy

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        self.policy.validate(request)
        started = time.perf_counter()
        env = os.environ.copy()
        env.update(request.env)
        process = await asyncio.create_subprocess_exec(
            *request.argv,
            cwd=request.cwd,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=request.timeout_seconds
            )
        except TimeoutError:
            process.kill()
            stdout, stderr = await process.communicate()
            return ExecutionResult(
                status="timeout",
                stdout=stdout.decode(errors="replace"),
                stderr=stderr.decode(errors="replace"),
                exit_code=process.returncode,
                duration_ms=int((time.perf_counter() - started) * 1000),
                timed_out=True,
            )

        return ExecutionResult(
            status="success" if process.returncode == 0 else "failed",
            stdout=stdout.decode(errors="replace"),
            stderr=stderr.decode(errors="replace"),
            exit_code=process.returncode,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
