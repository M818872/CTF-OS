from dataclasses import dataclass, field
from uuid import UUID, uuid4

from ctfos_sdk import Capability

from app.core.registry import CapabilityRegistry


@dataclass(slots=True)
class Investigation:
    id: UUID = field(default_factory=uuid4)
    objective: str = ""
    status: str = "created"
    tasks: list[str] = field(default_factory=list)


class InvestigationAgent:
    """Small orchestration layer; reasoning and execution stay behind interfaces."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self.registry = registry

    def create(self, objective: str) -> Investigation:
        objective = objective.strip()
        if not objective:
            raise ValueError("objective must not be empty")
        return Investigation(objective=objective, status="planned")

    def plan(self, investigation: Investigation, capabilities: list[str]) -> Investigation:
        for name in capabilities:
            if self.registry.get(name) is not None:
                investigation.tasks.append(name)
        investigation.status = "ready" if investigation.tasks else "blocked"
        return investigation

    def register_capability(self, name: str, description: str, provider: str) -> None:
        self.registry.register(Capability(name=name, description=description), provider)
