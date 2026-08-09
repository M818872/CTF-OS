from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.models import Base
from app.services.job_queue import JobQueue


async def _session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    return engine, async_sessionmaker(engine, expire_on_commit=False)


async def test_enqueue_claim_and_complete_job() -> None:
    engine, factory = await _session_factory()
    try:
        queue = JobQueue()
        async with factory() as session:
            job = await queue.enqueue(session, "terminal.execute", {"command": "printf hello"})
            await session.commit()
            job_id = job.id

        async with factory() as session:
            claimed = await queue.claim(session)
            assert claimed is not None
            assert claimed.id == job_id
            assert claimed.status == "running"
            assert claimed.attempts == 1
            await queue.complete(session, claimed, {"stdout": "hello"})

        async with factory() as session:
            completed = await queue.get(session, job_id)
            assert completed is not None
            assert completed.status == "completed"
            assert completed.result == {"stdout": "hello"}
    finally:
        await engine.dispose()


async def test_failed_job_requeues_until_attempt_limit() -> None:
    engine, factory = await _session_factory()
    try:
        queue = JobQueue()
        async with factory() as session:
            job = await queue.enqueue(
                session,
                "terminal.execute",
                {"command": "false"},
                max_attempts=2,
            )
            await session.commit()
            job_id = job.id

        async with factory() as session:
            claimed = await queue.claim(session)
            assert claimed is not None
            await queue.fail(session, claimed, "first failure")

        async with factory() as session:
            retried = await queue.get(session, job_id)
            assert retried is not None
            assert retried.status == "queued"
            assert retried.error == "first failure"
            retried.available_at = retried.created_at
            await session.commit()

        async with factory() as session:
            claimed_again = await queue.claim(session)
            assert claimed_again is not None
            await queue.fail(session, claimed_again, "second failure")

        async with factory() as session:
            failed = await queue.get(session, job_id)
            assert failed is not None
            assert failed.status == "failed"
            assert failed.attempts == 2
    finally:
        await engine.dispose()
