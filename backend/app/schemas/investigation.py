from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class InvestigationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    challenge_type: str = Field(default="unknown", max_length=50)
    input_text: str | None = None


class InvestigationRead(BaseModel):
    id: UUID
    title: str
    challenge_type: str
    status: str
    input_text: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ActivityRead(BaseModel):
    id: UUID
    kind: str
    action: str
    status: str
    details: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceRead(BaseModel):
    investigation: InvestigationRead
    specialists: list[str]
    capabilities: list[str]
    activities: list[ActivityRead]


class PlanRequest(BaseModel):
    goal: str | None = Field(default=None, max_length=5000)


class ExecuteRequest(BaseModel):
    capability: str
    input_text: str = Field(default="", max_length=10000)
