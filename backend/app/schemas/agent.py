from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class SolveChallengeRequest(BaseModel):
    challenge: str = Field(default="", max_length=20000)
    url: HttpUrl | None = None


class SolveChallengeResponse(BaseModel):
    id: UUID
    job_id: UUID
    status: str
    specialists: list[str]
    capabilities: list[str]
    flag: str | None = None
    message: str
