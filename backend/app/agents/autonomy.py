from dataclasses import dataclass

from app.specialists.catalog import SpecialistDefinition, SPECIALISTS, get_specialist


@dataclass(frozen=True, slots=True)
class AgentTask:
    goal: str
    specialist: str
    capabilities: tuple[str, ...]


class AutonomousRouter:
    """Small deterministic router; LLM reasoning can be attached without changing contracts."""

    _KEYWORDS: dict[str, tuple[str, ...]] = {
        "crypto": ("hash", "cipher", "encrypt", "decrypt", "base64", "xor", "rsa", "aes"),
        "web": ("http", "https", "website", "web", "api", "cookie", "login", "sql"),
        "forensics": ("pcap", "memory", "disk", "artifact", "metadata", "image", "file"),
        "reverse": ("binary", "elf", "exe", "reverse", "assembly", "disassemble"),
        "pwn": ("buffer overflow", "rop", "heap", "format string", "exploit"),
        "network": ("network", "packet", "traffic", "dns", "tcp", "udp"),
        "stego": ("steg", "hidden image", "png", "jpeg", "embedded"),
        "osint": ("osint", "username", "social", "domain", "person", "search"),
        "mobile": ("apk", "android", "mobile", "adb"),
        "blockchain": ("blockchain", "smart contract", "wallet", "transaction", "ethereum"),
    }

    def route(self, goal: str) -> tuple[AgentTask, ...]:
        text = goal.lower()
        matches: list[AgentTask] = []
        for specialist, keywords in self._KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                definition = get_specialist(specialist)
                if definition:
                    matches.append(AgentTask(goal, definition.name, definition.capabilities))
        if matches:
            return tuple(matches)
        fallback = get_specialist("misc")
        assert fallback is not None
        return (AgentTask(goal, fallback.name, fallback.capabilities),)

    def all_specialists(self) -> tuple[SpecialistDefinition, ...]:
        return SPECIALISTS
