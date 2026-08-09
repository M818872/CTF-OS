import pytest

from app.specialists.agents import get_agent, list_agents


def test_all_catalog_specialists_have_agents() -> None:
    agents = list_agents()
    assert len(agents) == 11
    assert {agent.name for agent in agents} >= {"crypto", "web", "forensics", "reverse", "pwn", "network", "stego", "osint", "mobile", "blockchain", "misc"}


def test_crypto_agent_executes_registered_capability() -> None:
    agent = get_agent("crypto")
    assert agent is not None
    action = agent.plan("48656c6c6f", "crypto.decode")
    result = agent.execute(action)
    assert result.specialist == "crypto"
    assert result.result.status == "completed"
    assert result.result.data["candidates"]["hex"] == "Hello"


def test_agent_rejects_capability_from_another_specialist() -> None:
    agent = get_agent("web")
    assert agent is not None
    with pytest.raises(ValueError, match="not registered"):
        agent.plan("https://example.test", "crypto.decode")


def test_agent_rejects_empty_input() -> None:
    agent = get_agent("web")
    assert agent is not None
    with pytest.raises(ValueError, match="input_text"):
        agent.plan("   ")


def test_unknown_agent_returns_none() -> None:
    assert get_agent("does-not-exist") is None
