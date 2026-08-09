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


@pytest.mark.asyncio
async def test_workflow_is_bounded() -> None:
    seen: list[str] = []

    async def runner(step: WorkflowStep) -> bool:
        seen.append(step.id)
        return True

    result = await WorkflowEngine(runner, max_steps=2).run(
        (WorkflowStep("one", "inspect"), WorkflowStep("two", "decode"), WorkflowStep("three", "extract"))
    )
    assert result.status == "success"
    assert result.completed == ("one", "two")
    assert seen == ["one", "two"]


@pytest.mark.asyncio
async def test_workflow_rejects_duplicate_step_ids() -> None:
    result = await WorkflowEngine(lambda _: _success()).run(
        (WorkflowStep("same", "inspect"), WorkflowStep("same", "decode"))
    )
    assert result.status == "failed"
    assert result.completed == ("same",)
    assert result.failed_step == "same"


@pytest.mark.asyncio
async def test_workflow_hook_tracks_lifecycle() -> None:
    events: list[tuple[str, str]] = []

    async def hook(step: WorkflowStep, event: str) -> None:
        events.append((step.id, event))

    result = await WorkflowEngine(lambda _: _success(), hook=hook).run(
        (WorkflowStep("one", "inspect"),)
    )
    assert result.status == "success"
    assert events == [("one", "started"), ("one", "completed")]


@pytest.mark.asyncio
async def test_runner_exception_becomes_failed_result() -> None:
    async def runner(_: WorkflowStep) -> bool:
        raise RuntimeError("tool failed")

    result = await WorkflowEngine(runner).run((WorkflowStep("one", "inspect"),))
    assert result.status == "failed"
    assert result.completed == ()
    assert result.failed_step == "one"


async def _success() -> bool:
    return True


def test_workflow_rejects_invalid_max_steps() -> None:
    with pytest.raises(ValueError, match="max_steps"):
        WorkflowEngine(lambda _: _success(), max_steps=0)
