from dataclasses import dataclass

from app.runtime.command_runner import CommandRunner
from app.runtime.result_parser import extract_tokens
from app.tools.registry import ToolResult, get_tool


@dataclass(frozen=True)
class ExecutionResult:
    capability: str
    result: ToolResult


@dataclass(frozen=True)
class TerminalExecutionResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    tokens: list[str]


class CapabilityExecutionService:
    """Route registered capabilities and expose the configured CTF runtime."""

    def __init__(self) -> None:
        self.runner = CommandRunner()

    def execute(self, capability: str, input_text: str) -> ExecutionResult:
        tool = get_tool(capability)
        if tool is None:
            raise ValueError(f"Unknown capability: {capability}")
        return ExecutionResult(capability=capability, result=tool.handler(input_text))

    async def execute_async(self, capability: str, input_text: str) -> ExecutionResult:
        if capability == "terminal.execute":
            terminal = await self.execute_terminal(input_text)
            status = "success" if terminal.returncode == 0 and not terminal.timed_out else "failed"
            return ExecutionResult(
                capability=capability,
                result=ToolResult(
                    status=status,
                    summary=terminal.stdout.strip() or terminal.stderr.strip() or "Terminal command completed with no output.",
                    data={
                        "command": terminal.command,
                        "returncode": terminal.returncode,
                        "stdout": terminal.stdout,
                        "stderr": terminal.stderr,
                        "timed_out": terminal.timed_out,
                        "tokens": terminal.tokens,
                    },
                ),
            )
        return self.execute(capability, input_text)

    async def execute_terminal(self, command: str) -> TerminalExecutionResult:
        result = await self.runner.run(command)
        combined = f"{result.stdout}\n{result.stderr}"
        return TerminalExecutionResult(
            command=result.command,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            timed_out=result.timed_out,
            tokens=extract_tokens(combined),
        )
