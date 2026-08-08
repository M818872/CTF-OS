from app.tools.kali.discovery import discover_installed
from app.tools.kali.profiles import profile_for_specialist


def test_web_profile_exists() -> None:
    profile = profile_for_specialist("web")
    assert profile is not None
    assert "curl" in profile.commands


def test_discovery_filters_unavailable_commands(monkeypatch) -> None:
    profile = profile_for_specialist("crypto")
    assert profile is not None
    monkeypatch.setattr("app.tools.kali.discovery.shutil.which", lambda command: "/usr/bin/x" if command == "openssl" else None)
    assert discover_installed(profile) == ("openssl",)
