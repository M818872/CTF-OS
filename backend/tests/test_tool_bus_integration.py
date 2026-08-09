from app.services.manager import GlobalManager
from app.specialists.catalog import SPECIALISTS
from app.tools.bus import ToolBus


def test_global_manager_default_orchestrator_uses_tool_bus() -> None:
    orchestrator = GlobalManager._default_orchestrator(max_steps=1)
    assert isinstance(orchestrator.executor, ToolBus)


def test_tool_bus_routes_every_catalog_capability() -> None:
    bus = ToolBus()
    for specialist in SPECIALISTS:
        for capability in specialist.capabilities:
            route = bus.route(capability)
            assert route.capability == capability
            assert route.specialist == specialist.name
