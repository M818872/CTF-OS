from dataclasses import dataclass

from ctfos_sdk import Capability


@dataclass(frozen=True, slots=True)
class RegisteredCapability:
    capability: Capability
    provider: str


class CapabilityRegistry:
    def __init__(self) -> None:
        self._items: dict[str, RegisteredCapability] = {}

    def register(self, capability: Capability, provider: str) -> None:
        if capability.name in self._items:
            raise ValueError(f"Capability already registered: {capability.name}")
        self._items[capability.name] = RegisteredCapability(capability, provider)

    def get(self, name: str) -> RegisteredCapability | None:
        return self._items.get(name)

    def list(self) -> tuple[RegisteredCapability, ...]:
        return tuple(self._items.values())
