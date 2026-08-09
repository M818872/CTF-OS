from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ToolRead(BaseModel):
    name: str
    description: str


class ExecuteCapabilityRequest(BaseModel):
    capability: str = Field(min_length=1, max_length=160)
    input_text: str = Field(default="", max_length=10000)


class ExecuteCapabilityResponse(BaseModel):
    capability: str
    status: str
    summary: str
    data: dict


class TerminalExecuteRequest(BaseModel):
    command: str = Field(min_length=1, max_length=4000)


class TerminalExecuteResponse(BaseModel):
    command: str
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    tokens: list[str]


class ExecutionJobCreate(BaseModel):
    command: str = Field(min_length=1, max_length=4000)
    investigation_id: UUID | None = None
    max_attempts: int = Field(default=3, ge=1, le=10)


class ExecutionJobRead(BaseModel):
    id: UUID
    investigation_id: UUID | None
    kind: str
    status: str
    payload: dict
    result: dict | None
    error: str | None
    attempts: int
    max_attempts: int
    available_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
