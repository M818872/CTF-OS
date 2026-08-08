from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.core.evidence import EvidenceStore


@dataclass(frozen=True, slots=True)
class InvestigationReport:
    investigation_id: UUID
    findings: tuple[str, ...]
    timeline: tuple[str, ...]

    def markdown(self) -> str:
        lines = [f"# CTF-OS Investigation {self.investigation_id}", "", "## Findings"]
        lines.extend(f"- {item}" for item in self.findings) or lines.append("- No findings")
        lines.extend(["", "## Timeline"])
        lines.extend(f"- {item}" for item in self.timeline) or lines.append("- No events")
        return "\n".join(lines) + "\n"


def build_report(investigation_id: UUID, store: EvidenceStore) -> InvestigationReport:
    findings = tuple(
        f"{item.kind}: {item.value} ({item.confidence:.0%})"
        for item in store.evidence(investigation_id)
    )
    timeline = tuple(
        f"{event.created_at.isoformat()} — {event.action} [{event.status}]"
        for event in store.timeline(investigation_id)
    )
    return InvestigationReport(investigation_id, findings, timeline)
