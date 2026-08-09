import re
from dataclasses import dataclass
from typing import Protocol

from app.persistence.runtime import RuntimeEventStore
from app.services.execution import CapabilityExecutionService
from app.services.memory import InvestigationMemory, MemoryEvent


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


_FLAG_PATTERN = re.compile(r"\b(?:CTF|FLAG|THM|HTB|PICOCTF)\{[^\r\n{}]{1,200}\}", re.IGNORECASE)


class AutonomousOrchestrator:
    """Runs a bounded observe -> decide -> execute loop with durable tracing."""

    def __init__(self, executor: CapabilityExecutionService, planner: Planner, max_steps: int = 12, memory: InvestigationMemory | None = None, store: RuntimeEventStore | None = None) -> None:
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        self.executor = executor
        self.planner = planner
        self.max_steps = max_steps
        self.memory = memory or InvestigationMemory()
        self.store = store

    async def run_async(self, goal: str, investigation_id=None) -> tuple[list[Observation], str | None]:
        observations: list[Observation] = []
        for _ in range(self.max_steps):
            action = self.planner.next_action(goal, observations)
            if action is None:
                break
            await self._record("action", action.capability, action.input_text, "started", "Capability execution started.", {}, investigation_id)
            result = await self.executor.execute_async(action.capability, action.input_text)
            observation = Observation(action.capability, result.result.status, result.result.summary, result.result.data)
            observations.append(observation)
            await self._record("observation", action.capability, action.input_text, result.result.status, result.result.summary, result.result.data, investigation_id)
            flag = self._find_flag(result.result.summary) or self._find_flag(result.result.data)
            if flag:
                await self._record("flag", action.capability, action.input_text, "found", "Candidate flag detected.", {"flag": flag}, investigation_id)
                return observations, flag
        return observations, None

    def run(self, goal: str, investigation_id=None) -> list[Observation]:
        """Backward-compatible synchronous API returning observations only."""
        observations: list[Observation] = []
        for _ in range(self.max_steps):
            action = self.planner.next_action(goal, observations)
            if action is None:
                break
            self.memory.append(MemoryEvent(investigation_id, "action", action.capability, action.input_text, "started", "Capability execution started.", {}))
            result = self.executor.execute(action.capability, action.input_text).result
            observation = Observation(action.capability, result.status, result.summary, result.data)
            observations.append(observation)
            self.memory.append(MemoryEvent(investigation_id, "observation", action.capability, action.input_text, result.status, result.summary, result.data))
            flag = self._find_flag(result.summary) or self._find_flag(result.data)
            if flag:
                self.memory.append(MemoryEvent(investigation_id, "flag", action.capability, action.input_text, "found", "Candidate flag detected.", {"flag": flag}))
                break
        return observations

    async def _record(self, event_type: str, capability: str, input_text: str, status: str, summary: str, data: dict, investigation_id=None) -> None:
        self.memory.append(MemoryEvent(investigation_id, event_type, capability, input_text, status, summary, data))
        if self.store is not None:
            await self.store.append(event_type, capability, input_text, status, summary, data, investigation_id)

    @classmethod
    def _find_flag(cls, value: object) -> str | None:
        if isinstance(value, str):
            match = _FLAG_PATTERN.search(value)
            return match.group(0) if match else None
        if isinstance(value, dict):
            for item in value.values():
                found = cls._find_flag(item)
                if found:
                    return found
        elif isinstance(value, (list, tuple)):
            for item in value:
                found = cls._find_flag(item)
                if found:
                    return found
        return None
