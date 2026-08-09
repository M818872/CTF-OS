from dataclasses import dataclass

from app.services.orchestrator import Action, Observation
from app.specialists.catalog import SPECIALISTS, SpecialistDefinition


@dataclass(frozen=True)
class StrategyRule:
    keywords: tuple[str, ...]
    specialists: tuple[str, ...]


class ObservationAwarePlanner:
    """Deterministic planner backed by the canonical specialist catalog."""

    def __init__(self, capabilities: list[str]) -> None:
        self.capabilities = tuple(capabilities)
        self.specialists = SPECIALISTS
        self.rules = (
            StrategyRule(("http", "web", "url", "website", "login", "cookie", "xss", "sql"), ("web",)),
            StrategyRule(("pcap", "packet", "network", "traffic", "dns", "tcp", "udp"), ("network", "forensics")),
            StrategyRule(("image", "png", "jpg", "jpeg", "steg", "hidden", "metadata"), ("stego", "forensics")),
            StrategyRule(("cipher", "encrypt", "decrypt", "hash", "base64", "rsa", "xor"), ("crypto",)),
            StrategyRule(("binary", "elf", "exe", "reverse", "assembly", "disassembly", "strings"), ("reverse", "pwn")),
            StrategyRule(("buffer", "overflow", "rop", "heap", "canary", "format string"), ("pwn", "reverse")),
            StrategyRule(("android", "apk", "mobile", "manifest", "dex"), ("mobile", "reverse")),
            StrategyRule(("blockchain", "transaction", "wallet", "contract", "ethereum", "bitcoin"), ("blockchain",)),
            StrategyRule(("username", "email", "domain", "osint", "social", "profile"), ("osint",)),
            StrategyRule(("file", "disk", "memory", "artifact", "forensic", "document"), ("forensics",)),
        )

    def next_action(self, goal: str, observations: list[Observation]) -> Action | None:
        if not goal.strip() or not self.capabilities:
            return None

        context = " ".join([goal, *(item.summary for item in observations), *(str(item.data) for item in observations)]).lower()
        preferred: list[str] = []
        for rule in self.rules:
            if any(keyword in context for keyword in rule.keywords):
                preferred.extend(rule.specialists)

        available = [specialist for specialist in self.specialists if any(capability in self.capabilities for capability in specialist.capabilities)]
        candidates = sorted(available, key=lambda specialist: self._specialist_score(specialist, preferred, context), reverse=True)

        for specialist in candidates:
            for capability in specialist.capabilities:
                if capability in self.capabilities and not self._recently_used(capability, observations):
                    return Action(capability=capability, input_text=self._next_input(goal, observations))
        return None

    @staticmethod
    def _specialist_score(specialist: SpecialistDefinition, preferred: list[str], context: str) -> tuple[int, int, str]:
        explicit = 1 if specialist.name in preferred else 0
        metadata = f"{specialist.name} {specialist.category} {specialist.description} {' '.join(specialist.capabilities)}".lower()
        context_hits = sum(1 for token in set(context.split()) if len(token) >= 4 and token in metadata)
        return explicit, context_hits, specialist.name

    @staticmethod
    def _recently_used(capability: str, observations: list[Observation]) -> bool:
        return any(item.capability == capability for item in observations[-2:])

    @staticmethod
    def _next_input(goal: str, observations: list[Observation]) -> str:
        if not observations:
            return goal
        last = observations[-1]
        return f"Goal: {goal}\nPrevious capability: {last.capability}\nPrevious result: {last.summary}\nData: {last.data}"
