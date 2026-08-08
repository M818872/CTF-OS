from uuid import UUID

from app.evidence.models import Evidence
from app.services.memory import InvestigationMemory, MemoryEvent


class InvestigationTrace:
    """Projects orchestration events into investigation evidence."""

    def __init__(self, memory: InvestigationMemory | None = None) -> None:
        self.memory = memory or InvestigationMemory()

    def record(self, event: MemoryEvent) -> None:
        self.memory.append(event)

    def evidence(self, investigation_id: UUID | None = None) -> list[Evidence]:
        evidence: list[Evidence] = []
        for event in self.memory.events(investigation_id):
            if event.event_type == "action":
                evidence.append(Evidence(
                    kind="tool_action",
                    value=event.input_text,
                    source=event.capability,
                    confidence=1.0,
                ))
            elif event.event_type == "observation":
                evidence.append(Evidence(
                    kind="tool_observation",
                    value=event.summary,
                    source=event.capability,
                    confidence=1.0 if event.status == "success" else 0.5,
                ))
            elif event.event_type == "flag":
                evidence.append(Evidence(
                    kind="flag_candidate",
                    value=str(event.data.get("flag", "")),
                    source=event.capability,
                    confidence=1.0,
                ))
        return evidence
