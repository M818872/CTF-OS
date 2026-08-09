from app.tools.registry import ToolResult, register_tool


@register_tool("terminal.execute", "Execute an argv-safe command in the configured CTF runtime.")
def terminal_execute(input_text: str) -> ToolResult:
    # Actual execution is asynchronous and is routed by CapabilityExecutionService.
    # This registry entry exists so planners can discover the capability.
    return ToolResult(
        status="dispatch",
        summary="Terminal command dispatched to the runtime executor.",
        data={"command": input_text.strip()},
    )


@register_tool("terminal.inspect", "Inspect terminal/runtime availability without executing a command.")
def terminal_inspect(input_text: str) -> ToolResult:
    return ToolResult(
        status="ready",
        summary="Terminal capability is registered and can be dispatched by the runtime.",
        data={"requested": bool(input_text.strip())},
    )
