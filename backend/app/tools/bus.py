from __future__ import annotations

from dataclasses import dataclass

from app.runtime.kali_executor import KaliExecutionResult, KaliToolExecutor
from app.services.execution import CapabilityExecutionService, ExecutionResult
from app.specialists.catalog import SPECIALISTS


@dataclass(frozen=True, slots=True)
class ToolRoute:
    specialist: str
    capability: str


class ToolBus(CapabilityExecutionService):
    """Single dispatch boundary for specialist capabilities and Kali runtime tools."""

    def __init__(
        self,
        execution: CapabilityExecutionService | None = None,
        kali: KaliToolExecutor | None = None,
    ) -> None:
        super().__init__()
        self._execution = execution
        self._kali = kali or KaliToolExecutor(self.runner)
        self._routes = {
            capability: ToolRoute(specialist=item.name, capability=capability)
            for item in SPECIALISTS
            for capability in item.capabilities
        }

    def route(self, capability: str) -> ToolRoute:
        route = self._routes.get(capability)
        if route is None:
            raise ValueError(f"Unknown capability: {capability}")
        return route

    def execute(self, capability: str, input_text: str) -> ExecutionResult:
        if not input_text.strip():
            raise ValueError("input_text is required")
        self.route(capability)
        if self._execution is not None:
            return self._execution.execute(capability, input_text)
        return super().execute(capability, input_text)

    async def execute_kali(
        self,
        tool_name: str,
        args: list[str],
        custom_install_command: str | None = None,
    ) -> KaliExecutionResult:
        """Run a cataloged Kali tool, provisioning it when configured to do so."""
        return await self._kali.run(tool_name, args, custom_install_command)

    def capabilities_for(self, specialist: str) -> tuple[str, ...]:
        return tuple(route.capability for route in self._routes.values() if route.specialist == specialist)
