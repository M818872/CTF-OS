from __future__ import annotations

from uuid import UUID

from app.core.evidence import Evidence, EvidenceStore, TimelineEvent
from app.specialists.crypto import CryptoSpecialist


class CryptoWorkflow:
    def __init__(self, store: EvidenceStore, specialist: CryptoSpecialist | None = None) -> None:
        self.store = store
        self.specialist = specialist or CryptoSpecialist()

    def run(self, investigation_id: UUID, value: str) -> tuple[Evidence, ...]:
        self.store.add_event(
            investigation_id,
            TimelineEvent(action="crypto.analyze", status="started", source="crypto"),
        )
        findings = self.specialist.analyze(value)
        evidence = tuple(
            self.store.add_evidence(
                investigation_id,
                Evidence(
                    kind=finding.kind,
                    value=finding.value,
                    source="crypto",
                    confidence=finding.confidence,
                ),
            )
            for finding in findings
        )
        self.store.add_event(
            investigation_id,
            TimelineEvent(
                action="crypto.analyze",
                status="completed",
                source="crypto",
                metadata={"findings": len(evidence)},
            ),
        )
        return evidence
