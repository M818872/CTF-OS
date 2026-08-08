from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.execution import CapabilityExecutionService
from app.services.orchestrator import AutonomousOrchestrator
from app.services.planner import DeterministicPlanner
from app.tools.registry import list_tools

router = APIRouter(prefix="/orchestration", tags=["orchestration"])


class RunRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=10000)
    max_steps: int = Field(default=8, ge=1, le=32)


class ObservationRead(BaseModel):
    capability: str
    status: str
    summary: str
    data: dict


class RunResponse(BaseModel):
    observations: list[ObservationRead]
    steps: int


@router.post("/run", response_model=RunResponse)
async def run_orchestration(payload: RunRequest) -> RunResponse:
    capabilities = [tool.name for tool in list_tools()]
    if not capabilities:
        raise HTTPException(status_code=503, detail="No capabilities are registered")

    planner = DeterministicPlanner(capabilities)
    orchestrator = AutonomousOrchestrator(CapabilityExecutionService(), planner, payload.max_steps)
    observations = orchestrator.run(payload.goal)
    return RunResponse(
        observations=[ObservationRead(**item.__dict__) for item in observations],
        steps=len(observations),
    )
