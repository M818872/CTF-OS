from __future__ import annotations

from dataclasses import dataclass

from app.specialists.catalog import SpecialistDefinition, get_specialist
from app.tools.bus import ToolBus
from app.tools.registry import ToolResult


@dataclass(frozen=True, slots=True)
class SpecialistAction:
    specialist: str
    capability: str
    input_text: str


@dataclass(frozen=True, slots=True)
class SpecialistResult:
    specialist: str
    capability: str
    result: ToolResult


class SpecialistAgent:
    """Expose one specialist domain through its catalog-approved tool bus."""

    def __init__(self, definition: SpecialistDefinition, bus: ToolBus | None = None) -> None:
        self.definition = definition
        self.bus = bus or ToolBus()

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def capabilities(self) -> tuple[str, ...]:
        return self.definition.capabilities

    def plan(self, input_text: str, capability: str | None = None) -> SpecialistAction:
        selected = capability or self.definition.capabilities[0]
        if selected not in self.definition.capabilities:
            raise ValueError(f"capability {selected!r} is not registered to {self.name!r}")
        if not input_text.strip():
            raise ValueError("input_text is required")
        return SpecialistAction(self.name, selected, input_text)

    def execute(self, action: SpecialistAction) -> SpecialistResult:
        if action.specialist != self.name:
            raise ValueError("action belongs to a different specialist")
        if action.capability not in self.definition.capabilities:
            raise ValueError(f"capability {action.capability!r} is not registered to {self.name!r}")
        result = self.bus.execute(action.capability, action.input_text)
        return SpecialistResult(self.name, action.capability, result.result)


def get_agent(name: str, bus: ToolBus | None = None) -> SpecialistAgent | None:
    definition = get_specialist(name)
    return SpecialistAgent(definition, bus) if definition is not None else None


def list_agents(bus: ToolBus | None = None) -> tuple[SpecialistAgent, ...]:
    from app.specialists.catalog import SPECIALISTS

    return tuple(SpecialistAgent(item, bus) for item in SPECIALISTS)
