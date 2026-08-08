from io import BytesIO
from uuid import uuid4

import pytest
from starlette.datastructures import Headers, UploadFile

from app.services.artifacts import MAX_ARTIFACT_BYTES, ingest_artifact


@pytest.mark.asyncio
async def test_ingest_artifact_records_sha256_and_size(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    payload = b"CTF-OS evidence"
    upload = UploadFile(BytesIO(payload), filename="sample.txt", headers=Headers({"content-type": "text/plain"}))

    artifact = await ingest_artifact(uuid4(), upload)

    assert artifact.filename == "sample.txt"
    assert artifact.size_bytes == len(payload)
    assert artifact.sha256 == "ec411a6f3b496e7a9290e4f2397506217342357a3680646839a1de556aff5578"


@pytest.mark.asyncio
async def test_ingest_artifact_rejects_oversized_upload(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    payload = b"x" * (MAX_ARTIFACT_BYTES + 1)
    upload = UploadFile(BytesIO(payload), filename="large.bin")

    with pytest.raises(ValueError, match="exceeds"):
        await ingest_artifact(uuid4(), upload)
