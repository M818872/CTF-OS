import pytest

from app.core.registry import CapabilityRegistry
from app.manager.agent import InvestigationAgent


def test_agent_plans_registered_capability() -> None:
    agent = InvestigationAgent(CapabilityRegistry())
    agent.register_capability("decode.base64", "Decode Base64", "crypto")

    investigation = agent.create("Analyze challenge artifact")
    result = agent.plan(investigation, ["decode.base64", "missing"])

    assert result.status == "ready"
    assert result.tasks == ["decode.base64"]


def test_agent_rejects_empty_objective() -> None:
    agent = InvestigationAgent(CapabilityRegistry())
    with pytest.raises(ValueError, match="objective"):
        agent.create("  ")
