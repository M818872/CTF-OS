from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ToolResult:
    status: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Capability:
    name: str
    description: str


class Plugin(Protocol):
    name: str
    version: str

    def capabilities(self) -> tuple[Capability, ...]: ...


class Specialist(Protocol):
    name: str

    def capabilities(self) -> tuple[Capability, ...]: ...
