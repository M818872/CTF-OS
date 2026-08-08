from fastapi import APIRouter, HTTPException

from app.schemas.execution import ExecuteCapabilityRequest, ExecuteCapabilityResponse, ToolRead
from app.services.execution import CapabilityExecutionService
from app.tools.registry import list_tools

router = APIRouter(prefix="/tools", tags=["tools"])
service = CapabilityExecutionService()


@router.get("", response_model=list[ToolRead])
async def available_tools() -> list[ToolRead]:
    return [ToolRead(name=tool.name, description=tool.description) for tool in list_tools()]


@router.post("/execute", response_model=ExecuteCapabilityResponse)
async def execute_tool(payload: ExecuteCapabilityRequest) -> ExecuteCapabilityResponse:
    try:
        execution = service.execute(payload.capability, payload.input_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ExecuteCapabilityResponse(
        capability=execution.capability,
        status=execution.result.status,
        summary=execution.result.summary,
        data=execution.result.data,
    )
