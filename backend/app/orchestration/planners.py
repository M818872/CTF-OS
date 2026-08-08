from app.orchestration.loop import Action, SolverState


class RegistryPlanner:
    """Small deterministic planner used until an external reasoning model is configured."""

    def __init__(self, capabilities: list[str]) -> None:
        self.capabilities = capabilities

    def next_action(self, state: SolverState) -> Action | None:
        used = {item.capability for item in state.actions}
        for capability in self.capabilities:
            if capability not in used:
                return Action(capability=capability, input_text=state.goal)
        return None
