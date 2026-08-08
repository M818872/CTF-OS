from __future__ import annotations

import hashlib
import re
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import UploadFile

from app.db.models import Artifact

MAX_ARTIFACT_BYTES = 10 * 1024 * 1024
STORAGE_ROOT = Path("data/artifacts")
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


async def ingest_artifact(investigation_id: UUID, upload: UploadFile) -> Artifact:
    filename = Path(upload.filename or "artifact.bin").name
    filename = _SAFE_NAME.sub("_", filename)[:255] or "artifact.bin"
    artifact_id = uuid4()
    storage_key = f"{investigation_id}/{artifact_id}"
    destination = STORAGE_ROOT / str(investigation_id) / str(artifact_id)
    destination.parent.mkdir(parents=True, exist_ok=True)

    digest = hashlib.sha256()
    size = 0
    try:
        with destination.open("wb") as output:
            while chunk := await upload.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_ARTIFACT_BYTES:
                    raise ValueError(f"artifact exceeds {MAX_ARTIFACT_BYTES} byte limit")
                digest.update(chunk)
                output.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()

    return Artifact(
        id=artifact_id,
        investigation_id=investigation_id,
        filename=filename,
        content_type=upload.content_type or "application/octet-stream",
        size_bytes=size,
        sha256=digest.hexdigest(),
        storage_key=storage_key,
    )
