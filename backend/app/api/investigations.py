from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
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


async def _get_investigation(investigation_id: UUID, session: AsyncSession) -> Investigation:
    investigation = await session.scalar(
        select(Investigation).where(Investigation.id == investigation_id)
    )
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return investigation


@router.get("", response_model=list[InvestigationRead])
async def list_investigations(
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> list[Investigation]:
    result = await session.scalars(select(Investigation).order_by(Investigation.created_at.desc()))
    return list(result.all())


@router.post("", response_model=InvestigationRead, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    payload: InvestigationCreate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Investigation:
    investigation = Investigation(**payload.model_dump())
    session.add(investigation)
    await session.commit()
    await session.refresh(investigation)
    return investigation


@router.get("/{investigation_id}", response_model=InvestigationRead)
async def get_investigation(
    investigation_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Investigation:
    return await _get_investigation(investigation_id, session)


@router.get("/{investigation_id}/workspace", response_model=WorkspaceRead)
async def get_workspace(
    investigation_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> WorkspaceRead:
    investigation = await _get_investigation(investigation_id, session)
    activities = await session.scalars(
        select(InvestigationActivity)
        .where(InvestigationActivity.investigation_id == investigation_id)
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


@router.post("/{investigation_id}/plan", response_model=WorkspaceRead)
async def plan_investigation(
    investigation_id: UUID,
    payload: PlanRequest,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> WorkspaceRead:
    investigation = await _get_investigation(investigation_id, session)
    goal = (payload.goal or investigation.input_text or investigation.title).strip()
    if not goal:
        raise HTTPException(status_code=400, detail="A goal or challenge input is required")

    tasks = router_agent.route(goal)
    existing = await session.scalars(
        select(InvestigationActivity).where(
            InvestigationActivity.investigation_id == investigation_id,
            InvestigationActivity.kind == "plan",
        )
    )
    if not list(existing.all()):
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
    return await get_workspace(investigation_id, session)


@router.post("/{investigation_id}/execute", response_model=WorkspaceRead)
async def execute_capability(
    investigation_id: UUID,
    payload: ExecuteRequest,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> WorkspaceRead:
    investigation = await _get_investigation(investigation_id, session)
    capability = payload.capability.strip()
    specialist_name = capability.split(".", 1)[0]
    specialist = get_specialist(specialist_name)
    if specialist is None or capability not in specialist.capabilities:
        raise HTTPException(status_code=400, detail="Unknown capability")

    # This MVP records an execution request and deliberately does not execute
    # arbitrary shell commands. Tool adapters can later plug into this boundary.
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
    return await get_workspace(investigation_id, session)
