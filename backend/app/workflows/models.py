from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    id: str
    capability: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class WorkflowResult:
    status: str
    completed: tuple[str, ...]
    failed_step: str | None = None
