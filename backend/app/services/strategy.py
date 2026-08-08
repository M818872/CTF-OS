from dataclasses import dataclass

from app.services.orchestrator import Action, Observation


@dataclass(frozen=True)
class StrategyRule:
    keywords: tuple[str, ...]
    preferred: tuple[str, ...]


class ObservationAwarePlanner:
    """Reproducible planner that changes strategy from observed results.

    This is intentionally deterministic: an LLM can implement the same
    Planner protocol later without changing the orchestration loop.
    """

    def __init__(self, capabilities: list[str]) -> None:
        self.capabilities = tuple(capabilities)
        self.rules = (
            StrategyRule(("http", "web", "url", "website", "login"), ("web", "analysis")),
            StrategyRule(("pcap", "packet", "network", "traffic"), ("network", "forensics")),
            StrategyRule(("image", "png", "jpg", "steg", "hidden"), ("stego", "forensics")),
            StrategyRule(("cipher", "encrypt", "decrypt", "hash", "base64"), ("crypto", "analysis")),
            StrategyRule(("binary", "elf", "exe", "reverse", "assembly"), ("reverse", "pwn")),
        )

    def next_action(self, goal: str, observations: list[Observation]) -> Action | None:
        if not goal.strip():
            return None
        available = list(self.capabilities)
        if not available:
            return None

        context = " ".join([goal, *(item.summary for item in observations)]).lower()
        preferred: list[str] = []
        for rule in self.rules:
            if any(keyword in context for keyword in rule.keywords):
                preferred.extend(rule.preferred)

        candidates = self._rank(available, preferred)
        for capability in candidates:
            if not self._recently_used(capability, observations):
                return Action(capability=capability, input_text=self._next_input(goal, observations))

        return None

    @staticmethod
    def _rank(available: list[str], preferred: list[str]) -> list[str]:
        def score(name: str) -> tuple[int, str]:
            lowered = name.lower()
            return (max((len(key) for key in preferred if key in lowered), default=0), name)

        return sorted(available, key=score, reverse=True)

    @staticmethod
    def _recently_used(capability: str, observations: list[Observation]) -> bool:
        return any(item.capability == capability for item in observations[-2:])

    @staticmethod
    def _next_input(goal: str, observations: list[Observation]) -> str:
        if not observations:
            return goal
        last = observations[-1]
        return f"Goal: {goal}\nPrevious capability: {last.capability}\nPrevious result: {last.summary}\nData: {last.data}"
