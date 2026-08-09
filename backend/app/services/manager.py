from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4

from app.services.execution import CapabilityExecutionService
from app.services.orchestrator import AutonomousOrchestrator
from app.services.strategy import ObservationAwarePlanner
from app.tools.registry import list_tools


class InvestigationStatus(StrEnum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class Investigation:
    id: UUID
    goal: str
    status: InvestigationStatus
    steps: int = 0
    flag: str | None = None


class GlobalManager:
    """Own the investigation lifecycle and delegate solving to orchestration."""

    def __init__(self, orchestrator_factory: Callable[[int], AutonomousOrchestrator] | None = None) -> None:
        self._investigations: dict[UUID, Investigation] = {}
        self._orchestrator_factory = orchestrator_factory or self._default_orchestrator

    def create(self, goal: str) -> Investigation:
        goal = goal.strip()
        if not goal:
            raise ValueError("goal is required")
        investigation = Investigation(uuid4(), goal, InvestigationStatus.CREATED)
        self._investigations[investigation.id] = investigation
        return investigation

    def get(self, investigation_id: UUID) -> Investigation | None:
        return self._investigations.get(investigation_id)

    async def run(self, investigation_id: UUID, max_steps: int = 8) -> Investigation:
        current = self._investigations.get(investigation_id)
        if current is None:
            raise KeyError(f"unknown investigation: {investigation_id}")
        if current.status == InvestigationStatus.RUNNING:
            raise RuntimeError("investigation is already running")
        if max_steps < 1:
            raise ValueError("max_steps must be positive")

        self._investigations[investigation_id] = Investigation(
            current.id, current.goal, InvestigationStatus.RUNNING, current.steps, current.flag
        )
        try:
            orchestrator = self._orchestrator_factory(max_steps)
            observations, flag = await orchestrator.run_async(current.goal, investigation_id)
            completed = Investigation(
                current.id,
                current.goal,
                InvestigationStatus.COMPLETED,
                len(observations),
                flag,
            )
            self._investigations[investigation_id] = completed
            return completed
        except Exception:
            failed = Investigation(
                current.id, current.goal, InvestigationStatus.FAILED, current.steps, current.flag
            )
            self._investigations[investigation_id] = failed
            raise

    @staticmethod
    def _default_orchestrator(max_steps: int) -> AutonomousOrchestrator:
        capabilities = [tool.name for tool in list_tools()]
        if not capabilities:
            raise RuntimeError("no capabilities are registered")
        return AutonomousOrchestrator(
            executor=CapabilityExecutionService(),
            planner=ObservationAwarePlanner(capabilities),
            max_steps=max_steps,
        )
