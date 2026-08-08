from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Investigation
from app.db.session import get_session
from app.schemas.investigation import InvestigationCreate, InvestigationRead

router = APIRouter(prefix="/investigations", tags=["investigations"])


@router.post("", response_model=InvestigationRead, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    payload: InvestigationCreate,
    session: AsyncSession = Depends(get_session),
) -> Investigation:
    investigation = Investigation(**payload.model_dump())
    session.add(investigation)
    await session.commit()
    await session.refresh(investigation)
    return investigation


@router.get("/{investigation_id}", response_model=InvestigationRead)
async def get_investigation(
    investigation_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Investigation:
    investigation = await session.scalar(
        select(Investigation).where(Investigation.id == investigation_id)
    )
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return investigation
