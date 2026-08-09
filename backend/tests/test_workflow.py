import pytest

from app.workflows.engine import WorkflowEngine
from app.workflows.models import WorkflowStep


@pytest.mark.asyncio
async def test_workflow_completes_all_steps() -> None:
    seen: list[str] = []

    async def runner(step: WorkflowStep) -> bool:
        seen.append(step.id)
        return True

    result = await WorkflowEngine(runner).run(
        (WorkflowStep("one", "inspect"), WorkflowStep("two", "decode"))
    )
    assert result.status == "success"
    assert result.completed == ("one", "two")
    assert result.failed_step is None
    assert seen == ["one", "two"]


@pytest.mark.asyncio
async def test_workflow_stops_on_failure() -> None:
    seen: list[str] = []

    async def runner(step: WorkflowStep) -> bool:
        seen.append(step.id)
        return step.id != "bad"

    result = await WorkflowEngine(runner).run(
        (WorkflowStep("good", "inspect"), WorkflowStep("bad", "decode"), WorkflowStep("later", "x"))
    )
    assert result.status == "failed"
    assert result.completed == ("good",)
    assert result.failed_step == "bad"
    assert seen == ["good", "bad"]


@pytest.mark.asyncio
async def test_workflow_handles_empty_plan() -> None:
    result = await WorkflowEngine(lambda _: _success()).run(())
    assert result.status == "success"
    assert result.completed == ()
    assert result.failed_step is None


async def _success() -> bool:
    return True
