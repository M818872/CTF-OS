from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, String, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class RuntimeEventRow(Base):
    __tablename__ = "runtime_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    investigation_id: Mapped[UUID | None] = mapped_column(index=True)
    event_type: Mapped[str] = mapped_column(String(32))
    capability: Mapped[str] = mapped_column(String(128))
    input_text: Mapped[str] = mapped_column(String(10000))
    status: Mapped[str] = mapped_column(String(32))
    summary: Mapped[str] = mapped_column(String(20000))
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class RuntimeEventStore:
    def __init__(self, database_url: str) -> None:
        self.engine = create_async_engine(database_url, pool_pre_ping=True)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)

    async def initialize(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def append(self, event_type: str, capability: str, input_text: str, status: str, summary: str, data: dict[str, Any], investigation_id: UUID | None = None) -> UUID:
        row = RuntimeEventRow(
            investigation_id=investigation_id,
            event_type=event_type,
            capability=capability,
            input_text=input_text,
            status=status,
            summary=summary,
            data=data,
        )
        async with self.sessions() as session:
            session.add(row)
            await session.commit()
            return row.id

    async def list_for_investigation(self, investigation_id: UUID) -> list[RuntimeEventRow]:
        async with self.sessions() as session:
            result = await session.execute(
                select(RuntimeEventRow)
                .where(RuntimeEventRow.investigation_id == investigation_id)
                .order_by(RuntimeEventRow.created_at.asc())
            )
            return list(result.scalars())

    async def close(self) -> None:
        await self.engine.dispose()
