from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.autonomy import AutonomousRouter
from app.db.models import Investigation, InvestigationActivity
from app.db.session import get_session
from app.schemas.agent import SolveChallengeResponse
from app.services.artifacts import ingest_artifact
from app.services.job_queue import JobQueue

router = APIRouter(prefix="/agent", tags=["agent"])
router_agent = AutonomousRouter()
queue = JobQueue()
Session = Annotated[AsyncSession, Depends(get_session)]


@router.post("/solve", response_model=SolveChallengeResponse, status_code=202)
async def solve_challenge(
    session: Session,
    challenge: Annotated[str, Form()] = "",
    url: Annotated[str | None, Form()] = None,
    file: Annotated[UploadFile | None, File()] = None,
) -> SolveChallengeResponse:
    challenge = challenge.strip()
    url = url.strip() if url else None
    if not challenge and not url and file is None:
        raise HTTPException(status_code=400, detail="Provide challenge text, a URL, or a file")

    parts = [item for item in (challenge, f"Target URL: {url}" if url else None) if item]
    title = "CTF challenge"
    uploaded_name = file.filename if file is not None else None
    investigation = Investigation(
        title=title,
        challenge_type="unknown",
        status="received",
        input_text="\n\n".join(parts) or f"Uploaded artifact: {uploaded_name}",
    )
    session.add(investigation)
    await session.flush()

    artifact_path: str | None = None
    if file is not None:
        try:
            artifact = await ingest_artifact(investigation.id, file)
        except ValueError as exc:
            raise HTTPException(status_code=413, detail=str(exc)) from exc
        session.add(artifact)
        artifact_path = f"data/artifacts/{artifact.storage_key}"
        session.add(InvestigationActivity(
            investigation_id=investigation.id,
            kind="artifact",
            action=f"Receive challenge file {artifact.filename}",
            status="received",
            details=f"size={artifact.size_bytes}; sha256={artifact.sha256}",
        ))

    goal = investigation.input_text or title
    tasks = router_agent.route(goal)
    investigation.challenge_type = tasks[0].specialist if tasks else "misc"
    investigation.status = "queued"

    job = await queue.enqueue(
        session,
        kind="ctf.solve",
        payload={
            "challenge": challenge,
            "url": url,
            "artifact_path": artifact_path,
        },
        investigation_id=investigation.id,
        max_attempts=2,
    )
    session.add(InvestigationActivity(
        investigation_id=investigation.id,
        kind="agent",
        action="Start autonomous CTF solve",
        status="queued",
        details="Route: " + ", ".join(task.specialist for task in tasks),
    ))
    await session.commit()

    specialists = list(dict.fromkeys(task.specialist for task in tasks))
    capabilities = list(dict.fromkeys(capability for task in tasks for capability in task.capabilities))
    return SolveChallengeResponse(
        id=investigation.id,
        job_id=job.id,
        status="queued",
        specialists=specialists,
        capabilities=capabilities,
        message="Challenge queued. The worker is now running the autonomous discovery loop.",
    )
