from uuid import uuid4

from app.evidence.models import Evidence
from app.evidence.store import EvidenceStore
from app.reports.generator import InvestigationReport
from app.timeline.models import Timeline, TimelineEvent


def test_evidence_timeline_report() -> None:
    investigation_id = uuid4()
    evidence_store = EvidenceStore()
    timeline = Timeline()
    evidence_store.add(investigation_id, Evidence("flag_candidate", "CTF{demo}", "crypto"))
    timeline.append(investigation_id, TimelineEvent("finding", "Candidate recorded", "crypto"))

    report = InvestigationReport(
        investigation_id,
        "Demo",
        evidence_store.list(investigation_id),
        timeline.list(investigation_id),
    )
    output = report.markdown()
    assert "CTF{demo}" in output
    assert "Candidate recorded" in output
