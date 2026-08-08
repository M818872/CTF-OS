from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolResult:
    status: str
    summary: str
    data: dict


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    handler: Callable[[str], ToolResult]


def _describe(input_text: str) -> ToolResult:
    return ToolResult(
        status="ready",
        summary="Capability accepted for controlled execution.",
        data={"input_length": len(input_text), "preview": input_text[:240]},
    )


TOOL_REGISTRY: dict[str, ToolDefinition] = {}


def register_tool(name: str, description: str) -> Callable:
    def decorator(handler: Callable[[str], ToolResult]) -> Callable[[str], ToolResult]:
        TOOL_REGISTRY[name] = ToolDefinition(name, description, handler)
        return handler

    return decorator


@register_tool("analysis.describe", "Record and normalize an investigation input.")
def describe(input_text: str) -> ToolResult:
    return _describe(input_text)


def get_tool(name: str) -> ToolDefinition | None:
    return TOOL_REGISTRY.get(name)


def list_tools() -> list[ToolDefinition]:
    return list(TOOL_REGISTRY.values())


# Import after registry primitives exist so decorators register specialist adapters.
from app.tools import specialists as _specialists  # noqa: F401
