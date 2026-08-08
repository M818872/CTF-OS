from app.specialists.catalog import SPECIALISTS, get_specialist


def test_all_primary_categories_are_registered() -> None:
    names = {item.name for item in SPECIALISTS}
    assert {"crypto", "web", "forensics", "reverse", "pwn", "network", "stego", "osint", "mobile", "blockchain", "misc"} <= names


def test_specialist_lookup() -> None:
    specialist = get_specialist("crypto")
    assert specialist is not None
    assert specialist.category == "cryptography"
    assert "crypto.detect" in specialist.capabilities
