from dataclasses import asdict

from app.toolbus.kali import KALI_TOOLS, KaliTool, installed_tools


def all_kali_tools() -> tuple[KaliTool, ...]:
    return KALI_TOOLS


def available_kali_tools() -> tuple[KaliTool, ...]:
    return installed_tools()


def kali_manifest() -> list[dict[str, str | None]]:
    return [asdict(tool) for tool in KALI_TOOLS]
