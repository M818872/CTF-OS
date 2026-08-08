import pytest

from app.tools.kali.runner import KaliRunner


def test_runner_rejects_non_allowlisted_command() -> None:
    with pytest.raises(PermissionError):
        KaliRunner({"printf"}).run(["sh", "-c", "echo unsafe"])


def test_runner_disables_shell_interpretation() -> None:
    result = KaliRunner({"printf"}).run(["printf", "hello"])
    assert result.returncode == 0
    assert result.stdout == "hello"
