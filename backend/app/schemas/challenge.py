from uuid import UUID

from pydantic import BaseModel, Field


class ChallengeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=50)
    objective: str = Field(min_length=1, max_length=4000)
    source: str | None = Field(default=None, max_length=500)


class ChallengeRead(ChallengeCreate):
    id: UUID
    status: str
