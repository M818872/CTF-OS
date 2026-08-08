import base64
import binascii
import hashlib
import re
from urllib.parse import urlparse

from app.tools.registry import ToolResult, register_tool


@register_tool("crypto.decode_base64", "Decode a Base64 text payload.")
def decode_base64(input_text: str) -> ToolResult:
    try:
        decoded = base64.b64decode(input_text.strip(), validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError) as exc:
        return ToolResult("error", "Input is not valid UTF-8 Base64.", {"error": str(exc)})
    return ToolResult("success", "Base64 payload decoded.", {"decoded": decoded})


@register_tool("crypto.hash_sha256", "Calculate SHA-256 for supplied text.")
def hash_sha256(input_text: str) -> ToolResult:
    digest = hashlib.sha256(input_text.encode()).hexdigest()
    return ToolResult("success", "SHA-256 calculated.", {"sha256": digest})


@register_tool("web.inspect_url", "Parse an HTTP(S) URL without making a network request.")
def inspect_url(input_text: str) -> ToolResult:
    parsed = urlparse(input_text.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ToolResult("error", "Input is not a valid HTTP(S) URL.", {})
    return ToolResult("success", "URL parsed without network access.", {"scheme": parsed.scheme, "host": parsed.hostname, "port": parsed.port, "path": parsed.path or "/"})


@register_tool("forensics.identify_text", "Identify common text encodings and hashes heuristically.")
def identify_text(input_text: str) -> ToolResult:
    value = input_text.strip()
    candidates: list[str] = []
    if re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", value) and len(value) % 4 == 0:
        candidates.append("base64")
    if re.fullmatch(r"[0-9a-fA-F]+", value) and len(value) % 2 == 0:
        candidates.append("hex")
    if re.fullmatch(r"[0-9a-fA-F]{32}", value): candidates.append("md5")
    if re.fullmatch(r"[0-9a-fA-F]{40}", value): candidates.append("sha1")
    if re.fullmatch(r"[0-9a-fA-F]{64}", value): candidates.append("sha256")
    return ToolResult("success", "Text fingerprinted without external execution.", {"candidates": candidates})


@register_tool("misc.decode_hex", "Decode a hexadecimal payload.")
def decode_hex(input_text: str) -> ToolResult:
    try:
        decoded = bytes.fromhex(input_text.strip()).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        return ToolResult("error", "Input is not valid UTF-8 hexadecimal.", {"error": str(exc)})
    return ToolResult("success", "Hex payload decoded.", {"decoded": decoded})
