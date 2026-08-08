from __future__ import annotations

import base64
import binascii
import re
from dataclasses import dataclass
from urllib.parse import unquote


@dataclass(frozen=True, slots=True)
class Finding:
    kind: str
    value: str
    confidence: float


_HASH_PATTERNS = (
    ("md5", re.compile(r"^[0-9a-fA-F]{32}$")),
    ("sha1", re.compile(r"^[0-9a-fA-F]{40}$")),
    ("sha256", re.compile(r"^[0-9a-fA-F]{64}$")),
    ("sha512", re.compile(r"^[0-9a-fA-F]{128}$")),
)


class CryptoSpecialist:
    name = "crypto"

    def analyze(self, value: str) -> tuple[Finding, ...]:
        value = value.strip()
        findings: list[Finding] = []
        findings.extend(self._hashes(value))
        findings.extend(self._encodings(value))
        if value.isalpha() and len(value) >= 4:
            findings.append(Finding("rot13", _rot13(value), 0.35))
        return tuple(findings)

    def _hashes(self, value: str) -> list[Finding]:
        return [Finding(kind, value, 0.95) for kind, pattern in _HASH_PATTERNS if pattern.fullmatch(value)]

    def _encodings(self, value: str) -> list[Finding]:
        findings: list[Finding] = []
        if re.fullmatch(r"(?:[0-9a-fA-F]{2})+", value):
            try:
                decoded = bytes.fromhex(value).decode("utf-8")
                findings.append(Finding("hex", decoded, 0.90))
            except (ValueError, UnicodeDecodeError):
                pass
        if re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", value) and len(value) % 4 == 0:
            try:
                decoded = base64.b64decode(value, validate=True).decode("utf-8")
                findings.append(Finding("base64", decoded, 0.90))
            except (binascii.Error, UnicodeDecodeError):
                pass
        decoded_url = unquote(value)
        if decoded_url != value:
            findings.append(Finding("url", decoded_url, 0.85))
        return findings


def _rot13(value: str) -> str:
    out: list[str] = []
    for char in value:
        base = ord("A") if char.isupper() else ord("a")
        out.append(chr((ord(char) - base + 13) % 26 + base) if char.isalpha() else char)
    return "".join(out)
