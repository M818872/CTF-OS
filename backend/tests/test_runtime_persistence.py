from uuid import uuid4

import pytest

from app.persistence.runtime import RuntimeEventStore


@pytest.mark.asyncio
async def test_runtime_event_round_trip(tmp_path) -> None:
    store = RuntimeEventStore(f"sqlite+aiosqlite:///{tmp_path / 'runtime.db'}")
    await store.initialize()
    investigation_id = uuid4()

    event_id = await store.append(
        "observation",
        "crypto.decode",
        "SGVsbG8=",
        "success",
        "decoded",
        {"value": "Hello"},
        investigation_id,
    )
    events = await store.list_for_investigation(investigation_id)

    assert event_id == events[0].id
    assert events[0].event_type == "observation"
    assert events[0].capability == "crypto.decode"
    assert events[0].data == {"value": "Hello"}

    await store.close()
