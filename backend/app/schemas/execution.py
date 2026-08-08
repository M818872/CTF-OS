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
