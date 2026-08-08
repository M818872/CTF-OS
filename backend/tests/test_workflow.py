from app.workflows.engine import WorkflowEngine
from app.workflows.models import WorkflowStep


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
    assert seen == ["one", "two"]


async def test_workflow_stops_on_failure() -> None:
    async def runner(step: WorkflowStep) -> bool:
        return step.id != "bad"

    result = await WorkflowEngine(runner).run(
        (WorkflowStep("good", "inspect"), WorkflowStep("bad", "decode"), WorkflowStep("later", "x"))
    )
    assert result.status == "failed"
    assert result.completed == ("good",)
    assert result.failed_step == "bad"
