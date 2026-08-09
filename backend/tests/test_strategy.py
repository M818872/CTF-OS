from app.services.orchestrator import Observation
from app.services.strategy import ObservationAwarePlanner


def test_web_goal_selects_web_capability() -> None:
    planner = ObservationAwarePlanner(["web.inspect", "web.enumerate", "crypto.analyze"])
    action = planner.next_action("Find the login endpoint and inspect the web application", [])
    assert action is not None
    assert action.capability == "web.inspect"


def test_pcap_goal_selects_network_capability() -> None:
    planner = ObservationAwarePlanner(["network.identify", "network.extract", "crypto.analyze"])
    action = planner.next_action("Analyze this PCAP traffic", [])
    assert action is not None
    assert action.capability == "network.identify"


def test_previous_capability_is_avoided() -> None:
    planner = ObservationAwarePlanner(["crypto.detect", "crypto.decode"])
    observations = [Observation("crypto.detect", "completed", "Crypto input inspected.", {})]
    action = planner.next_action("Decode this base64 value", observations)
    assert action is not None
    assert action.capability == "crypto.decode"
