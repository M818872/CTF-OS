from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from app.db.models import ExecutionJob
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession


LEASE_SECONDS = 300


class JobQueue:
    """Durable execution queue backed by PostgreSQL row locking.

    Redis remains available for future event fan-out, while PostgreSQL is the
    source of truth so queued work survives API and worker restarts.
    """

    async def enqueue(
        self,
        session: AsyncSession,
        kind: str,
        payload: dict[str, Any],
        investigation_id: UUID | None = None,
        max_attempts: int = 3,
    ) -> ExecutionJob:
        if not kind.strip():
            raise ValueError("job kind is required")
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        job = ExecutionJob(
            kind=kind.strip(),
            payload=payload,
            investigation_id=investigation_id,
            max_attempts=max_attempts,
        )
        session.add(job)
        await session.flush()
        return job

    async def get(self, session: AsyncSession, job_id: UUID) -> ExecutionJob | None:
        return await session.scalar(select(ExecutionJob).where(ExecutionJob.id == job_id))

    async def claim(self, session: AsyncSession) -> ExecutionJob | None:
        while True:
            now = datetime.now(UTC)
            stale_before = now - timedelta(seconds=LEASE_SECONDS)
            query = (
                select(ExecutionJob)
                .where(
                    or_(
                        (ExecutionJob.status == "queued") & (ExecutionJob.available_at <= now),
                        (ExecutionJob.status == "running") & (ExecutionJob.locked_at <= stale_before),
                    )
                )
                .order_by(ExecutionJob.created_at.asc())
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            job = await session.scalar(query)
            if job is None:
                return None
            if job.status == "running" and job.attempts >= job.max_attempts:
                job.status = "failed"
                job.error = "execution lease expired after the retry limit was reached"
                job.finished_at = now
                job.locked_at = None
                await session.commit()
                continue
            job.status = "running"
            job.locked_at = now
            job.started_at = job.started_at or now
            job.attempts += 1
            await session.commit()
            await session.refresh(job)
            return job

    async def complete(self, session: AsyncSession, job: ExecutionJob, result: dict[str, Any]) -> None:
        job.status = "completed"
        job.result = result
        job.error = None
        job.locked_at = None
        job.finished_at = datetime.now(UTC)
        await session.commit()

    async def fail(self, session: AsyncSession, job: ExecutionJob, error: str) -> None:
        job.error = error[:10000]
        job.locked_at = None
        if job.attempts < job.max_attempts:
            job.status = "queued"
            job.available_at = datetime.now(UTC) + timedelta(seconds=min(2**job.attempts, 60))
        else:
            job.status = "failed"
            job.finished_at = datetime.now(UTC)
        await session.commit()
