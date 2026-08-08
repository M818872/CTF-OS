from app.services.orchestrator import Action, Observation


class DeterministicPlanner:
    """Small baseline planner used until an LLM planner is configured.

    It never invents capabilities: every action comes from the supplied
    allow-list and the sequence is deterministic for reproducible tests.
    """

    def __init__(self, capabilities: list[str]) -> None:
        self.capabilities = tuple(capabilities)

    def next_action(self, goal: str, observations: list[Observation]) -> Action | None:
        if not goal.strip():
            return None
        index = len(observations)
        if index >= len(self.capabilities):
            return None
        return Action(capability=self.capabilities[index], input_text=goal)
