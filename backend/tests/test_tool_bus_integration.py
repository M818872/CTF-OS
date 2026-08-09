from app.services.manager import GlobalManager
from app.tools.bus import ToolBus


def test_global_manager_default_orchestrator_uses_tool_bus() -> None:
    orchestrator = GlobalManager._default_orchestrator(max_steps=1)
    assert isinstance(orchestrator.executor, ToolBus)


def test_tool_bus_routes_every_catalog_capability() -> None:
    bus = ToolBus()
    for capability in (
        "crypto.decode",
        "web.inspect",
        "forensics.triage",
        "reverse.inspect",
        "pwn.check",
        "network.inspect",
        "stego.extract",
        "osint.lookup",
        "mobile.inspect",
        "blockchain.inspect",
        "analysis.describe",
    ):
        route = bus.route(capability)
        assert route.capability == capability
        assert route.specialist
