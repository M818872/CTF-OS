from fastapi import APIRouter

from app.core.registry import CapabilityRegistry
from app.specialists.catalog import SPECIALISTS

router = APIRouter(prefix="/capabilities", tags=["capabilities"])

_registry = CapabilityRegistry()
for specialist in SPECIALISTS:
    for capability in specialist.capabilities:
        _registry.register(
            capability=__import__("ctfos_sdk", fromlist=["Capability"]).Capability(
                name=capability,
                description=f"{specialist.name}: {specialist.description}",
            ),
            provider=specialist.name,
        )


@router.get("")
async def list_capabilities() -> list[dict[str, str]]:
    return [
        {
            "name": item.capability.name,
            "description": item.capability.description,
            "provider": item.provider,
        }
        for item in _registry.list()
    ]


@router.get("/specialists")
async def list_specialists() -> list[dict[str, object]]:
    return [
        {
            "name": item.name,
            "category": item.category,
            "description": item.description,
            "capabilities": list(item.capabilities),
        }
        for item in SPECIALISTS
    ]
