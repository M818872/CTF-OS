from uuid import uuid4

from app.core.evidence import EvidenceStore
from app.specialists.crypto_workflow import CryptoWorkflow


def test_crypto_workflow_records_evidence_and_timeline() -> None:
    investigation_id = uuid4()
    store = EvidenceStore()
    evidence = CryptoWorkflow(store).run(investigation_id, "68656c6c6f")

    assert evidence[0].kind == "hex"
    assert evidence[0].value == "hello"
    assert len(store.timeline(investigation_id)) == 2
