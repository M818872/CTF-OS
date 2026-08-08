from app.specialists.crypto import CryptoSpecialist


def test_detects_base64() -> None:
    findings = CryptoSpecialist().analyze("Y3RmLW9z")
    assert any(f.kind == "base64" and f.value == "ctf-os" for f in findings)


def test_detects_hex() -> None:
    findings = CryptoSpecialist().analyze("637466")
    assert any(f.kind == "hex" and f.value == "ctf" for f in findings)


def test_detects_hash_shape() -> None:
    findings = CryptoSpecialist().analyze("a" * 64)
    assert any(f.kind == "sha256" for f in findings)


def test_rot13_candidate() -> None:
    findings = CryptoSpecialist().analyze("uryyb")
    assert any(f.kind == "rot13" and f.value == "hello" for f in findings)
