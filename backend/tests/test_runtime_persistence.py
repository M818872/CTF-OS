import pytest

from app.persistence.runtime import RuntimeEventStore


@pytest.mark.asyncio
async def test_runtime_event_round_trip(tmp_path) -> None:
    store = RuntimeEventStore(f"sqlite+aiosqlite:///{tmp_path / 'runtime.db'}")
    await store.initialize()
    event_id = await store.append("observation", "crypto.decode", "SGVsbG8=", "success", "decoded", {"value": "Hello"})

    async with store.sessions() as session:
        assert event_id is not None

    await store.close()
