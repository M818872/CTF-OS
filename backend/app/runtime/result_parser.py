from __future__ import annotations

import re

_TOKEN = re.compile(r"\b[A-Z0-9_]+\{[^\n\r{}]{1,512}\}")


def extract_tokens(text: str) -> list[str]:
    """Extract common CTF-style challenge tokens from tool output."""
    values: list[str] = []
    for match in _TOKEN.findall(text):
        if match not in values:
            values.append(match)
    return values
