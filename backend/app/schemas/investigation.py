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
