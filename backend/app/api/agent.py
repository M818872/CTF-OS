from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.autonomy import AutonomousRouter
from app.db.models import Investigation, InvestigationActivity
from app.db.session import get_session
from app.schemas.agent import SolveChallengeResponse
from app.services.artifacts import ingest_artifact

router = APIRouter(prefix="/agent", tags=["agent"])
router_agent = AutonomousRouter()
Session = Annotated[AsyncSession, Depends(get_session)]


@router.post("/solve", response_model=SolveChallengeResponse)
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
    investigation = Investigation(
        title=title,
        challenge_type="unknown",
        status="received",
        input_text="\n\n".join(parts) or f"Uploaded artifact: {file.filename}",
    )
    session.add(investigation)
    await session.flush()

    if file is not None:
        try:
            artifact = await ingest_artifact(investigation.id, file)
        except ValueError as exc:
            raise HTTPException(status_code=413, detail=str(exc)) from exc
        session.add(artifact)
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
    investigation.status = "planned"
    session.add(InvestigationActivity(
        investigation_id=investigation.id,
        kind="agent",
        action="Start autonomous CTF solve",
        status="ready",
        details="Route: " + ", ".join(task.specialist for task in tasks),
    ))
    await session.commit()

    specialists = list(dict.fromkeys(task.specialist for task in tasks))
    capabilities = list(dict.fromkeys(capability for task in tasks for capability in task.capabilities))
    return SolveChallengeResponse(
        id=investigation.id,
        status=investigation.status,
        specialists=specialists,
        capabilities=capabilities,
        message="Challenge received. The agent has classified the input and prepared the solve route.",
    )
