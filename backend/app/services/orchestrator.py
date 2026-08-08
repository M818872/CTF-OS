from dataclasses import dataclass
from typing import Protocol

from app.services.execution import CapabilityExecutionService


@dataclass(frozen=True)
class Observation:
    capability: str
    status: str
    summary: str
    data: dict


@dataclass(frozen=True)
class Action:
    capability: str
    input_text: str


class Planner(Protocol):
    def next_action(self, goal: str, observations: list[Observation]) -> Action | None: ...


class AutonomousOrchestrator:
    """Runs a bounded observe -> decide -> execute loop.

    The planner decides what registered capability to call next. The
    orchestrator owns iteration limits and records every observation, so a
    planner cannot accidentally create an unbounded execution loop.
    """

    def __init__(self, executor: CapabilityExecutionService, planner: Planner, max_steps: int = 12) -> None:
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        self.executor = executor
        self.planner = planner
        self.max_steps = max_steps

    def run(self, goal: str) -> list[Observation]:
        observations: list[Observation] = []
        for _ in range(self.max_steps):
            action = self.planner.next_action(goal, observations)
            if action is None:
                break
            result = self.executor.execute(action.capability, action.input_text).result
            observation = Observation(
                capability=action.capability,
                status=result.status,
                summary=result.summary,
                data=result.data,
            )
            observations.append(observation)
            if self._contains_flag(result.data) or self._contains_flag(result.summary):
                break
        return observations

    @staticmethod
    def _contains_flag(value: object) -> bool:
        if isinstance(value, str):
            lowered = value.lower()
            return "flag{" in lowered or "ctf{" in lowered or "thm{" in lowered or "picoctf{" in lowered
        if isinstance(value, dict):
            return any(AutonomousOrchestrator._contains_flag(item) for item in value.values())
        if isinstance(value, (list, tuple)):
            return any(AutonomousOrchestrator._contains_flag(item) for item in value)
        return False
