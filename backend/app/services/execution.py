from dataclasses import dataclass

from app.tools.registry import ToolResult, get_tool


@dataclass(frozen=True)
class ExecutionResult:
    capability: str
    result: ToolResult


class CapabilityExecutionService:
    """Controlled execution boundary for specialist capabilities.

    The MVP only invokes registered Python handlers. No shell, subprocess,
    network scanning, or arbitrary command execution is performed here.
    """

    def execute(self, capability: str, input_text: str) -> ExecutionResult:
        tool = get_tool(capability)
        if tool is None:
            raise ValueError(f"Unknown capability: {capability}")
        return ExecutionResult(capability=capability, result=tool.handler(input_text))
