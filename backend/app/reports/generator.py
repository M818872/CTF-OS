from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.evidence.models import Evidence
from app.timeline.models import TimelineEvent


@dataclass(frozen=True, slots=True)
class InvestigationReport:
    investigation_id: UUID
    title: str
    findings: tuple[Evidence, ...]
    timeline: tuple[TimelineEvent, ...]

    def markdown(self) -> str:
        lines = [f"# {self.title}", "", f"Investigation: `{self.investigation_id}`", "", "## Findings"]
        if not self.findings:
            lines.append("- No findings recorded.")
        else:
            lines.extend(
                f"- **{item.kind}** — {item.value} (confidence {item.confidence:.2f}; source `{item.source}`)"
                for item in self.findings
            )
        lines.extend(["", "## Timeline"])
        if not self.timeline:
            lines.append("- No timeline events recorded.")
        else:
            lines.extend(
                f"- `{event.created_at.isoformat()}` **{event.event_type}** — {event.message} (`{event.source}`)"
                for event in self.timeline
            )
        return "\n".join(lines) + "\n"
