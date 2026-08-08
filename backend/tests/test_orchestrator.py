from app.services.orchestrator import AutonomousOrchestrator
from app.services.planner import DeterministicPlanner
from app.tools.registry import ToolResult


class FakeExecutor:
    def execute(self, capability: str, input_text: str):
        class Result:
            def __init__(self):
                self.result = ToolResult(status="ok", summary=f"ran {capability}", data={"input": input_text})

        return Result()


def test_orchestrator_runs_until_plan_exhausted():
    planner = DeterministicPlanner(["analysis.describe", "analysis.describe"])
    observations = AutonomousOrchestrator(FakeExecutor(), planner, max_steps=4).run("solve challenge")
    assert len(observations) == 2
    assert all(item.status == "ok" for item in observations)


def test_orchestrator_respects_step_limit():
    planner = DeterministicPlanner(["analysis.describe"] * 5)
    observations = AutonomousOrchestrator(FakeExecutor(), planner, max_steps=2).run("solve challenge")
    assert len(observations) == 2


def test_flag_detection_stops_loop():
    class FlagExecutor(FakeExecutor):
        def execute(self, capability: str, input_text: str):
            class Result:
                result = ToolResult(status="ok", summary="found flag{demo}", data={})
            return Result()

    planner = DeterministicPlanner(["analysis.describe", "analysis.describe"])
    observations = AutonomousOrchestrator(FlagExecutor(), planner, max_steps=4).run("solve")
    assert len(observations) == 1
