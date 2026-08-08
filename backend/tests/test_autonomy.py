from app.agents.autonomy import AutonomousRouter


def test_routes_crypto_and_web_goals() -> None:
    tasks = AutonomousRouter().route("inspect this web API and decode the base64 hash")
    names = {task.specialist for task in tasks}
    assert {"web", "crypto"}.issubset(names)


def test_unknown_goal_uses_misc() -> None:
    tasks = AutonomousRouter().route("solve this unusual puzzle")
    assert tasks[0].specialist == "misc"
