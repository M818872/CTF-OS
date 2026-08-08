from dataclasses import dataclass
import shutil
import subprocess


@dataclass(frozen=True, slots=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    command: tuple[str, ...]


class KaliRunner:
    """Execute only explicitly allow-listed Kali binaries in a controlled workspace.

    The caller supplies an executable name, never a shell command string. Shell
    interpretation is disabled and the binary must exist in PATH.
    """

    def __init__(self, allowed: set[str], timeout: int = 30) -> None:
        self.allowed = frozenset(allowed)
        self.timeout = timeout

    def run(self, command: list[str], cwd: str | None = None) -> CommandResult:
        if not command:
            raise ValueError("command is required")
        executable = command[0]
        if executable not in self.allowed:
            raise PermissionError(f"command not allow-listed: {executable}")
        path = shutil.which(executable)
        if path is None:
            raise FileNotFoundError(executable)
        try:
            completed = subprocess.run(
                [path, *command[1:]],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"command timed out after {self.timeout}s") from exc
        return CommandResult(completed.returncode, completed.stdout, completed.stderr, tuple(command))
