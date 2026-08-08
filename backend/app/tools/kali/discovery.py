import shutil

from app.tools.kali.profiles import ToolProfile


def discover_installed(profile: ToolProfile) -> tuple[str, ...]:
    """Return only commands from a profile that exist in the current environment."""
    return tuple(command for command in profile.commands if shutil.which(command))
