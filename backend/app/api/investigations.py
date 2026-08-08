from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.autonomy import AutonomousRouter
from app.db.models import Investigation, InvestigationActivity
from app.db.session import get_session
from app.schemas.investigation import (
    ActivityRead,
    ExecuteRequest,
    InvestigationCreate,
    InvestigationRead,
    PlanRequest,
    WorkspaceRead,
)
from app.specialists.catalog import get_specialist

router = APIRouter(prefix="/investigations", tags=["investigations"])
router_agent = AutonomousRouter()
Session = Annotated[AsyncSession, Depends(get_session)]


async def _get_investigation(investigation_id: UUID, session: AsyncSession) -> Investigation:
    investigation = await session.scalar(select(Investigation).where(Investigation.id == investigation_id))
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return investigation


async def _workspace(investigation: Investigation, session: AsyncSession) -> WorkspaceRead:
    activities = await session.scalars(
        select(InvestigationActivity)
        .where(InvestigationActivity.investigation_id == investigation.id)
        .order_by(InvestigationActivity.created_at.asc())
    )
    tasks = router_agent.route(investigation.input_text or investigation.title)
    specialists = list(dict.fromkeys(task.specialist for task in tasks))
    capabilities = list(dict.fromkeys(capability for task in tasks for capability in task.capabilities))
    return WorkspaceRead(
        investigation=InvestigationRead.model_validate(investigation),
        specialists=specialists,
        capabilities=capabilities,
        activities=[ActivityRead.model_validate(item) for item in activities.all()],
    )


@router.get("", response_model=list[InvestigationRead])
async def list_investigations(session: Session) -> list[Investigation]:
    result = await session.scalars(select(Investigation).order_by(Investigation.created_at.desc()))
    return list(result.all())


@router.post("", response_model=InvestigationRead, status_code=status.HTTP_201_CREATED)
async def create_investigation(payload: InvestigationCreate, session: Session) -> Investigation:
    data = payload.model_dump()
    if data["challenge_type"] == "unknown":
        tasks = router_agent.route(data["input_text"] or data["title"])
        data["challenge_type"] = tasks[0].specialist if tasks else "misc"
    investigation = Investigation(**data)
    session.add(investigation)
    await session.commit()
    await session.refresh(investigation)
    return investigation


@router.get("/{investigation_id}", response_model=InvestigationRead)
async def get_investigation(investigation_id: UUID, session: Session) -> Investigation:
    return await _get_investigation(investigation_id, session)


@router.get("/{investigation_id}/workspace", response_model=WorkspaceRead)
async def get_workspace(investigation_id: UUID, session: Session) -> WorkspaceRead:
    return await _workspace(await _get_investigation(investigation_id, session), session)


@router.post("/{investigation_id}/plan", response_model=WorkspaceRead)
async def plan_investigation(investigation_id: UUID, payload: PlanRequest, session: Session) -> WorkspaceRead:
    investigation = await _get_investigation(investigation_id, session)
    goal = (payload.goal or investigation.input_text or investigation.title).strip()
    if not goal:
        raise HTTPException(status_code=400, detail="A goal or challenge input is required")
    tasks = router_agent.route(goal)
    existing = await session.scalar(
        select(InvestigationActivity.id).where(
            InvestigationActivity.investigation_id == investigation_id,
            InvestigationActivity.kind == "plan",
        )
    )
    if existing is None:
        session.add(
            InvestigationActivity(
                investigation_id=investigation_id,
                kind="plan",
                action="Create investigation plan",
                status="completed",
                details="Route: " + ", ".join(task.specialist for task in tasks),
            )
        )
        for task in tasks:
            session.add(
                InvestigationActivity(
                    investigation_id=investigation_id,
                    kind="capability",
                    action=f"Prepare {task.specialist} specialist",
                    status="ready",
                    details=", ".join(task.capabilities),
                )
            )
    investigation.status = "planned"
    await session.commit()
    return await _workspace(investigation, session)


@router.post("/{investigation_id}/execute", response_model=WorkspaceRead)
async def execute_capability(investigation_id: UUID, payload: ExecuteRequest, session: Session) -> WorkspaceRead:
    investigation = await _get_investigation(investigation_id, session)
    capability = payload.capability.strip()
    specialist = get_specialist(capability.split(".", 1)[0])
    if specialist is None or capability not in specialist.capabilities:
        raise HTTPException(status_code=400, detail="Unknown capability")
    session.add(
        InvestigationActivity(
            investigation_id=investigation_id,
            kind="execution",
            action=f"Run capability {capability}",
            status="queued",
            details=payload.input_text.strip() or "No input supplied",
        )
    )
    investigation.status = "in_progress"
    await session.commit()
    return await _workspace(investigation, session)


@router.get("/{investigation_id}/report", response_class=PlainTextResponse)
async def get_report(investigation_id: UUID, session: Session) -> str:
    investigation = await _get_investigation(investigation_id, session)
    activities = await session.scalars(
        select(InvestigationActivity)
        .where(InvestigationActivity.investigation_id == investigation_id)
        .order_by(InvestigationActivity.created_at.asc())
    )
    lines = [
        f"# CTF-OS Investigation: {investigation.title}",
        "",
        f"Status: {investigation.status}",
        f"Challenge type: {investigation.challenge_type}",
        "",
        "## Timeline",
    ]
    events = list(activities.all())
    lines.extend(
        f"- {event.created_at.isoformat()} — {event.action} [{event.status}]"
        + (f" — {event.details}" if event.details else "")
        for event in events
    )
    if not events:
        lines.append("- No activity recorded")
    return "\n".join(lines) + "\n"
