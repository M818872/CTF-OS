import pytest

from app.services.manager import GlobalManager, InvestigationStatus
from app.tools.bus import ToolBus


class FakeOrchestrator:
    async def run_async(self, goal: str, investigation_id):
        assert goal == "solve challenge"
        assert investigation_id is not None
        return [object(), object()], "CTF{manager_test}"


def test_create_normalizes_goal() -> None:
    manager = GlobalManager(lambda _: FakeOrchestrator())
    investigation = manager.create("  solve challenge  ")
    assert investigation.goal == "solve challenge"
    assert investigation.status == InvestigationStatus.CREATED
    assert manager.get(investigation.id) == investigation


def test_default_orchestrator_uses_tool_bus() -> None:
    orchestrator = GlobalManager._default_orchestrator(2)
    assert isinstance(orchestrator.executor, ToolBus)


@pytest.mark.asyncio
async def test_run_transitions_to_completed() -> None:
    manager = GlobalManager(lambda _: FakeOrchestrator())
    investigation = manager.create("solve challenge")
    result = await manager.run(investigation.id, max_steps=4)
    assert result.status == InvestigationStatus.COMPLETED
    assert result.steps == 2
    assert result.flag == "CTF{manager_test}"
    assert manager.get(investigation.id) == result


@pytest.mark.asyncio
async def test_run_failure_is_recorded() -> None:
    class FailingOrchestrator:
        async def run_async(self, goal: str, investigation_id):
            raise RuntimeError("planner failed")

    manager = GlobalManager(lambda _: FailingOrchestrator())
    investigation = manager.create("solve challenge")
    with pytest.raises(RuntimeError, match="planner failed"):
        await manager.run(investigation.id)
    assert manager.get(investigation.id).status == InvestigationStatus.FAILED


def test_invalid_goal_is_rejected() -> None:
    manager = GlobalManager()
    with pytest.raises(ValueError, match="goal is required"):
        manager.create("   ")
