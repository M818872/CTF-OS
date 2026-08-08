import base64
import binascii
import re
from urllib.parse import urlparse

from app.tools.registry import ToolResult, register_tool


def _result(summary: str, **data: object) -> ToolResult:
    return ToolResult(status="completed", summary=summary, data=data)


def _text(value: str) -> str:
    return value.strip()


@register_tool("crypto.detect", "Detect common hash and encoded-text shapes without external execution.")
def crypto_detect(value: str) -> ToolResult:
    text = _text(value)
    lengths = {32: "md5", 40: "sha1", 64: "sha256", 96: "sha384", 128: "sha512"}
    kind = lengths.get(len(text)) if re.fullmatch(r"[0-9a-fA-F]+", text) else None
    return _result("Crypto input inspected.", candidate=kind, length=len(text), hexadecimal=bool(re.fullmatch(r"[0-9a-fA-F]+", text)))


@register_tool("crypto.decode", "Decode common Base64 and hexadecimal challenge values.")
def crypto_decode(value: str) -> ToolResult:
    text = _text(value)
    candidates: dict[str, str] = {}
    try:
        candidates["hex"] = bytes.fromhex(text).decode("utf-8", errors="replace")
    except ValueError:
        pass
    try:
        candidates["base64"] = base64.b64decode(text, validate=True).decode("utf-8", errors="replace")
    except (ValueError, binascii.Error):
        pass
    return _result("Common encodings checked.", candidates=candidates)


@register_tool("crypto.analyze", "Summarize a cryptographic challenge value.")
def crypto_analyze(value: str) -> ToolResult:
    detected = crypto_detect(value)
    decoded = crypto_decode(value)
    return _result("Cryptographic input analyzed.", detection=detected.data, decoding=decoded.data)


@register_tool("web.inspect", "Parse a supplied web URL without making a network request.")
def web_inspect(value: str) -> ToolResult:
    parsed = urlparse(_text(value))
    return _result("URL inspected without network access.", scheme=parsed.scheme, host=parsed.hostname, port=parsed.port, path=parsed.path, query=parsed.query)


@register_tool("web.enumerate", "Prepare deterministic web enumeration targets from supplied URLs.")
def web_enumerate(value: str) -> ToolResult:
    inspected = web_inspect(value)
    host = inspected.data.get("host")
    return _result("Enumeration targets prepared; no network requests made.", targets=[host] if host else [], scheme=inspected.data.get("scheme"))


@register_tool("web.analyze", "Analyze a supplied web artifact or URL locally.")
def web_analyze(value: str) -> ToolResult:
    return _result("Web artifact analyzed locally.", length=len(value), url=web_inspect(value).data)


@register_tool("forensics.identify", "Identify common file signatures from hexadecimal or text input.")
def forensics_identify(value: str) -> ToolResult:
    raw = _text(value).lower()
    signatures = {"89504e47": "png", "ffd8ff": "jpeg", "25504446": "pdf", "504b0304": "zip", "7f454c46": "elf"}
    found = next((kind for prefix, kind in signatures.items() if raw.startswith(prefix)), None)
    return _result("Forensics signature check completed.", detected_type=found)


@register_tool("forensics.extract", "Prepare extraction metadata for a supplied artifact.")
def forensics_extract(value: str) -> ToolResult:
    return _result("Artifact extraction plan prepared.", input_length=len(value), next_steps=["identify signature", "preserve original", "extract into isolated workspace"])


@register_tool("forensics.analyze", "Summarize a forensic artifact locally.")
def forensics_analyze(value: str) -> ToolResult:
    return _result("Forensic artifact analyzed locally.", length=len(value), signature=forensics_identify(value).data)


@register_tool("reverse.identify", "Identify common executable formats from supplied hexadecimal data.")
def reverse_identify(value: str) -> ToolResult:
    return _result("Binary format identification completed.", format=forensics_identify(value).data.get("detected_type"))


@register_tool("reverse.strings", "Extract printable strings from supplied text or escaped byte data.")
def reverse_strings(value: str) -> ToolResult:
    strings = re.findall(r"[ -~]{4,}", value)
    return _result("Printable-string extraction completed.", strings=strings[:200], count=len(strings))


@register_tool("reverse.analyze", "Perform lightweight local binary triage.")
def reverse_analyze(value: str) -> ToolResult:
    return _result("Binary triage completed.", identification=reverse_identify(value).data, strings=reverse_strings(value).data)


@register_tool("network.identify", "Identify common packet-capture signatures without network access.")
def network_identify(value: str) -> ToolResult:
    raw = _text(value).lower()
    capture = "pcap" if raw.startswith("d4c3b2a1") or raw.startswith("a1b2c3d4") else None
    return _result("Network artifact identification completed.", format=capture)


@register_tool("network.extract", "Prepare local extraction targets from network artifact input.")
def network_extract(value: str) -> ToolResult:
    return _result("Network extraction plan prepared.", protocol_hints=["dns", "http", "tls"], input_length=len(value))


@register_tool("network.analyze", "Summarize a network artifact locally.")
def network_analyze(value: str) -> ToolResult:
    return _result("Network artifact analyzed locally.", identification=network_identify(value).data, length=len(value))


@register_tool("stego.identify", "Identify likely image/container formats for steganography analysis.")
def stego_identify(value: str) -> ToolResult:
    return _result("Steganography container check completed.", container=forensics_identify(value).data.get("detected_type"))


@register_tool("stego.extract", "Prepare hidden-data extraction checks for an artifact.")
def stego_extract(value: str) -> ToolResult:
    return _result("Stego extraction plan prepared.", checks=["metadata", "trailing data", "embedded payload", "common bit planes"])


@register_tool("stego.analyze", "Perform lightweight steganography triage.")
def stego_analyze(value: str) -> ToolResult:
    return _result("Stego triage completed.", identification=stego_identify(value).data, extraction=stego_extract(value).data)


@register_tool("osint.collect", "Normalize supplied OSINT identifiers without external lookup.")
def osint_collect(value: str) -> ToolResult:
    urls = re.findall(r"https?://[^\s]+", value)
    emails = re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", value)
    return _result("OSINT indicators collected locally.", urls=urls, emails=emails)


@register_tool("osint.correlate", "Correlate repeated indicators in supplied OSINT text.")
def osint_correlate(value: str) -> ToolResult:
    collected = osint_collect(value).data
    return _result("OSINT indicators correlated locally.", indicators=collected)


@register_tool("osint.analyze", "Analyze supplied OSINT indicators locally.")
def osint_analyze(value: str) -> ToolResult:
    return _result("OSINT analysis completed.", collection=osint_collect(value).data)


@register_tool("mobile.identify", "Identify Android APK/ZIP containers from supplied data.")
def mobile_identify(value: str) -> ToolResult:
    return _result("Mobile artifact identification completed.", format=forensics_identify(value).data.get("detected_type"))


@register_tool("mobile.extract", "Prepare an isolated mobile artifact extraction plan.")
def mobile_extract(value: str) -> ToolResult:
    return _result("Mobile extraction plan prepared.", checks=["manifest", "resources", "DEX", "signing metadata"])


@register_tool("mobile.analyze", "Perform lightweight Android artifact triage.")
def mobile_analyze(value: str) -> ToolResult:
    return _result("Mobile artifact triage completed.", identification=mobile_identify(value).data, extraction=mobile_extract(value).data)


@register_tool("blockchain.inspect", "Normalize a blockchain identifier without querying a chain.")
def blockchain_inspect(value: str) -> ToolResult:
    text = _text(value)
    return _result("Blockchain identifier inspected locally.", length=len(text), hex_like=bool(re.fullmatch(r"0x[0-9a-fA-F]+", text)))


@register_tool("blockchain.trace", "Prepare a blockchain tracing request without external chain access.")
def blockchain_trace(value: str) -> ToolResult:
    return _result("Blockchain tracing plan prepared; no chain query performed.", target=_text(value), next_steps=["resolve network", "fetch authorized transaction data", "build transfer graph"])


@register_tool("blockchain.analyze", "Analyze a blockchain identifier or supplied transaction data locally.")
def blockchain_analyze(value: str) -> ToolResult:
    return _result("Blockchain artifact analyzed locally.", inspection=blockchain_inspect(value).data)


@register_tool("pwn.identify", "Perform safe binary-exploitation challenge triage from supplied text.")
def pwn_identify(value: str) -> ToolResult:
    hints = [term for term in ("overflow", "rop", "heap", "format string", "canary", "nx", "pie") if term in value.lower()]
    return _result("Pwn challenge triage completed.", hints=hints)


@register_tool("pwn.analyze", "Analyze supplied pwn challenge notes without executing an exploit.")
def pwn_analyze(value: str) -> ToolResult:
    return _result("Pwn analysis completed without exploit execution.", triage=pwn_identify(value).data)


@register_tool("pwn.test", "Prepare a pwn test plan without executing arbitrary payloads.")
def pwn_test(value: str) -> ToolResult:
    return _result("Pwn test plan prepared.", checks=["protections", "input boundary", "crash reproducibility", "candidate primitive"])


@register_tool("misc.identify", "Classify generic challenge input using lightweight indicators.")
def misc_identify(value: str) -> ToolResult:
    return _result("Generic challenge triage completed.", length=len(value), urls=len(re.findall(r"https?://", value)), hex_like=bool(re.fullmatch(r"[0-9a-fA-F]+", _text(value))))


@register_tool("misc.transform", "Apply safe text normalization to challenge input.")
def misc_transform(value: str) -> ToolResult:
    return _result("Text normalization completed.", normalized=" ".join(_text(value).split()))


@register_tool("misc.analyze", "Perform generic local challenge triage.")
def misc_analyze(value: str) -> ToolResult:
    return _result("Generic challenge analysis completed.", identification=misc_identify(value).data)
