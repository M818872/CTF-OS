from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from app.services.orchestrator import AutonomousOrchestrator, Observation


class WorkflowPhase(StrEnum):
    PLAN = "plan"
    EXECUTE = "execute"
    OBSERVE = "observe"
    VERIFY = "verify"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class WorkflowState:
    investigation_id: UUID
    goal: str
    phase: WorkflowPhase = WorkflowPhase.PLAN
    step: int = 0
    observations: tuple[Observation, ...] = ()
    flag: str | None = None
    error: str | None = None


class WorkflowRunner(Protocol):
    async def run_async(self, goal: str, investigation_id: UUID) -> tuple[list[Observation], str | None]: ...


class InvestigationWorkflow:
    """Own the deterministic lifecycle around an autonomous orchestration run."""

    def __init__(self, runner: WorkflowRunner | None = None, max_steps: int = 8) -> None:
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        self.runner = runner
        self.max_steps = max_steps

    async def run(self, state: WorkflowState) -> WorkflowState:
        if not state.goal.strip():
            return WorkflowState(state.investigation_id, state.goal, WorkflowPhase.FAILED, state.step, error="goal is required")

        running = WorkflowState(state.investigation_id, state.goal, WorkflowPhase.EXECUTE, state.step, state.observations)
        try:
            runner = self.runner or self._default_runner()
            observations, flag = await runner.run_async(state.goal, state.investigation_id)
            phase = WorkflowPhase.COMPLETED if flag else WorkflowPhase.VERIFY
            return WorkflowState(
                state.investigation_id,
                state.goal,
                phase,
                len(observations),
                tuple(observations),
                flag,
            )
        except Exception as exc:
            return WorkflowState(
                running.investigation_id,
                running.goal,
                WorkflowPhase.FAILED,
                running.step,
                running.observations,
                error=str(exc),
            )

    def _default_runner(self) -> AutonomousOrchestrator:
        from app.services.execution import CapabilityExecutionService
        from app.services.strategy import ObservationAwarePlanner
        from app.tools.registry import list_tools

        capabilities = [tool.name for tool in list_tools()]
        if not capabilities:
            raise RuntimeError("no capabilities are registered")
        return AutonomousOrchestrator(
            executor=CapabilityExecutionService(),
            planner=ObservationAwarePlanner(capabilities),
            max_steps=self.max_steps,
        )
