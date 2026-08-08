from dataclasses import dataclass, field
import re
from typing import Protocol


@dataclass(frozen=True)
class Action:
    capability: str
    input_text: str


@dataclass(frozen=True)
class Observation:
    capability: str
    status: str
    summary: str
    data: dict
    flag: str | None = None


@dataclass
class SolverState:
    goal: str
    observations: list[Observation] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    flag: str | None = None


class Planner(Protocol):
    def next_action(self, state: SolverState) -> Action | None: ...


_FLAG_PATTERNS = (
    re.compile(r"\b(?:CTF|FLAG|THM|HTB)\{[^\r\n{}]{1,200}\}"),
)


def detect_flag(text: str) -> str | None:
    for pattern in _FLAG_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(0)
    return None


class SolverLoop:
    def __init__(self, planner: Planner, executor, max_steps: int = 20) -> None:
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        self.planner = planner
        self.executor = executor
        self.max_steps = max_steps

    def run(self, goal: str) -> SolverState:
        state = SolverState(goal=goal)
        for _ in range(self.max_steps):
            action = self.planner.next_action(state)
            if action is None:
                break
            state.actions.append(action)
            result = self.executor(action.capability, action.input_text)
            combined = f"{result.summary}\n{result.data}"
            flag = detect_flag(combined)
            observation = Observation(
                capability=action.capability,
                status=result.status,
                summary=result.summary,
                data=result.data,
                flag=flag,
            )
            state.observations.append(observation)
            if flag:
                state.flag = flag
                break
        return state
