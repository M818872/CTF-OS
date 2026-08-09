from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.execution import (
    ExecuteCapabilityRequest,
    ExecuteCapabilityResponse,
    ExecutionJobCreate,
    ExecutionJobRead,
    TerminalExecuteRequest,
    TerminalExecuteResponse,
    ToolRead,
)
from app.services.execution import CapabilityExecutionService
from app.services.job_queue import JobQueue
from app.tools.registry import list_tools

router = APIRouter(prefix="/tools", tags=["tools"])
service = CapabilityExecutionService()
queue = JobQueue()
Session = Annotated[AsyncSession, Depends(get_session)]


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


@router.post("/terminal", response_model=TerminalExecuteResponse)
async def execute_terminal(payload: TerminalExecuteRequest) -> TerminalExecuteResponse:
    try:
        result = await service.execute_terminal(payload.command)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return TerminalExecuteResponse(
        command=result.command,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        timed_out=result.timed_out,
        tokens=result.tokens,
    )


@router.post("/terminal/jobs", response_model=ExecutionJobRead, status_code=202)
async def enqueue_terminal_job(payload: ExecutionJobCreate, session: Session) -> ExecutionJobRead:
    if payload.investigation_id is not None:
        from app.db.models import Investigation
        from sqlalchemy import select

        exists = await session.scalar(select(Investigation.id).where(Investigation.id == payload.investigation_id))
        if exists is None:
            raise HTTPException(status_code=404, detail="Investigation not found")

    job = await queue.enqueue(
        session,
        kind="terminal.execute",
        payload={"command": payload.command},
        investigation_id=payload.investigation_id,
        max_attempts=payload.max_attempts,
    )
    await session.commit()
    await session.refresh(job)
    return job


@router.get("/jobs/{job_id}", response_model=ExecutionJobRead)
async def get_execution_job(job_id: UUID, session: Session) -> ExecutionJobRead:
    job = await queue.get(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Execution job not found")
    return job
