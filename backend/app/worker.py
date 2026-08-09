from __future__ import annotations

import asyncio
import logging
import os

from app.db.models import Base
from app.db.session import engine, session_factory
from app.services.execution import CapabilityExecutionService
from app.services.job_queue import JobQueue

LOGGER = logging.getLogger("ctf_os.worker")
POLL_SECONDS = float(os.getenv("CTF_OS_WORKER_POLL_SECONDS", "1"))


class ExecutionWorker:
    def __init__(self) -> None:
        self.queue = JobQueue()
        self.executor = CapabilityExecutionService()

    async def initialize(self) -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def process_once(self) -> bool:
        async with session_factory() as session:
            job = await self.queue.claim(session)
        if job is None:
            return False

        try:
            if job.kind != "terminal.execute":
                raise ValueError(f"unsupported execution job kind: {job.kind}")
            command = str(job.payload.get("command", ""))
            result = await self.executor.execute_terminal(command)
            result_data = {
                "command": result.command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timed_out": result.timed_out,
                "tokens": result.tokens,
            }
            async with session_factory() as session:
                current = await self.queue.get(session, job.id)
                if current is not None:
                    await self.queue.complete(session, current, result_data)
        except Exception as exc:
            LOGGER.exception("execution job failed", extra={"job_id": str(job.id)})
            async with session_factory() as session:
                current = await self.queue.get(session, job.id)
                if current is not None:
                    await self.queue.fail(session, current, str(exc))
        return True

    async def run_forever(self) -> None:
        await self.initialize()
        LOGGER.info("CTF-OS execution worker started")
        while True:
            processed = await self.process_once()
            if not processed:
                await asyncio.sleep(POLL_SECONDS)


async def main() -> None:
    try:
        await ExecutionWorker().run_forever()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
