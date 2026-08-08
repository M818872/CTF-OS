from uuid import UUID

from app.evidence.models import Evidence
from app.evidence.store import EvidenceStore
from app.tools.registry import ToolResult


class EvidenceService:
    def __init__(self, store: EvidenceStore | None = None) -> None:
        self.store = store or EvidenceStore()

    def record_tool_result(self, investigation_id: UUID, capability: str, result: ToolResult) -> Evidence:
        evidence = Evidence(
            kind="tool_result",
            value=result.summary,
            source=capability,
            confidence=1.0 if result.status == "success" else 0.7,
        )
        return self.store.add(investigation_id, evidence)
