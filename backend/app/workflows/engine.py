from __future__ import annotations

from collections.abc import Awaitable, Callable

from app.workflows.models import WorkflowResult, WorkflowStep

CapabilityRunner = Callable[[WorkflowStep], Awaitable[bool]]


class WorkflowEngine:
    def __init__(self, runner: CapabilityRunner) -> None:
        self.runner = runner

    async def run(self, steps: tuple[WorkflowStep, ...]) -> WorkflowResult:
        completed: list[str] = []
        for step in steps:
            ok = await self.runner(step)
            if not ok:
                return WorkflowResult("failed", tuple(completed), step.id)
            completed.append(step.id)
        return WorkflowResult("success", tuple(completed))
