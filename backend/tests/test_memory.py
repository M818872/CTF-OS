from app.memory.models import MemoryItem, SharedMemory


def test_memory_preserves_cross_agent_findings() -> None:
    memory = SharedMemory()
    memory.remember(MemoryItem("finding", "encoded payload", "forensics", 0.9))
    memory.remember(MemoryItem("finding", "decoded flag candidate", "crypto", 0.95))

    findings = memory.by_kind("finding")
    assert len(findings) == 2
    assert findings[0].source == "forensics"
    assert findings[1].source == "crypto"
