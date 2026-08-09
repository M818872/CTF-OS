from __future__ import annotations

from collections.abc import Awaitable, Callable

from app.workflows.models import WorkflowResult, WorkflowStep

CapabilityRunner = Callable[[WorkflowStep], Awaitable[bool]]
StepHook = Callable[[WorkflowStep, str], Awaitable[None]]


class WorkflowEngine:
    """Execute a planned sequence with bounded progress and observable lifecycle."""

    def __init__(self, runner: CapabilityRunner, max_steps: int | None = None, hook: StepHook | None = None) -> None:
        if max_steps is not None and max_steps < 1:
            raise ValueError("max_steps must be positive")
        self.runner = runner
        self.max_steps = max_steps
        self.hook = hook

    async def run(self, steps: tuple[WorkflowStep, ...]) -> WorkflowResult:
        completed: list[str] = []
        seen: set[str] = set()
        bounded_steps = steps if self.max_steps is None else steps[: self.max_steps]

        for step in bounded_steps:
            if not step.id or step.id in seen:
                return WorkflowResult("failed", tuple(completed), step.id or "duplicate")
            seen.add(step.id)
            if self.hook is not None:
                await self.hook(step, "started")
            try:
                ok = await self.runner(step)
            except (RuntimeError, ValueError, TypeError):
                if self.hook is not None:
                    await self.hook(step, "failed")
                return WorkflowResult("failed", tuple(completed), step.id)
            if not ok:
                if self.hook is not None:
                    await self.hook(step, "failed")
                return WorkflowResult("failed", tuple(completed), step.id)
            completed.append(step.id)
            if self.hook is not None:
                await self.hook(step, "completed")

        return WorkflowResult("success", tuple(completed))
