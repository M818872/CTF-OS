from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KaliTool:
    name: str
    binary: str
    category: str
    purpose: str


# The catalog describes tools available to the CTF runtime. Actual execution
# continues through the existing argv-safe CommandRunner.
KALI_TOOLS: tuple[KaliTool, ...] = (
    KaliTool("nmap", "nmap", "network", "host and service enumeration"),
    KaliTool("masscan", "masscan", "network", "high-speed port discovery"),
    KaliTool("curl", "curl", "web", "HTTP interaction"),
    KaliTool("wget", "wget", "web", "HTTP retrieval"),
    KaliTool("gobuster", "gobuster", "web", "directory and DNS enumeration"),
    KaliTool("ffuf", "ffuf", "web", "web fuzzing"),
    KaliTool("nikto", "nikto", "web", "web server assessment"),
    KaliTool("sqlmap", "sqlmap", "web", "SQL injection testing"),
    KaliTool("dig", "dig", "network", "DNS queries"),
    KaliTool("whois", "whois", "osint", "domain registration lookup"),
    KaliTool("tcpdump", "tcpdump", "network", "packet capture"),
    KaliTool("tshark", "tshark", "network", "packet analysis"),
    KaliTool("wireshark", "wireshark", "network", "graphical packet analysis"),
    KaliTool("file", "file", "forensics", "file identification"),
    KaliTool("strings", "strings", "forensics", "string extraction"),
    KaliTool("xxd", "xxd", "forensics", "hex inspection"),
    KaliTool("binwalk", "binwalk", "forensics", "embedded-file analysis"),
    KaliTool("exiftool", "exiftool", "forensics", "metadata extraction"),
    KaliTool("dd", "dd", "forensics", "raw data acquisition"),
    KaliTool("readelf", "readelf", "reverse", "ELF inspection"),
    KaliTool("objdump", "objdump", "reverse", "binary inspection"),
    KaliTool("nm", "nm", "reverse", "symbol inspection"),
    KaliTool("gdb", "gdb", "reverse", "debugging"),
    KaliTool("radare2", "radare2", "reverse", "binary analysis"),
    KaliTool("checksec", "checksec", "pwn", "binary mitigation inspection"),
    KaliTool("ROPgadget", "ROPgadget", "pwn", "ROP gadget discovery"),
    KaliTool("openssl", "openssl", "crypto", "cryptographic operations"),
    KaliTool("python3", "python3", "analysis", "scripted analysis"),
    KaliTool("git", "git", "analysis", "repository inspection"),
    KaliTool("steghide", "steghide", "stego", "steganography extraction"),
    KaliTool("stegseek", "stegseek", "stego", "steganography extraction"),
    KaliTool("zsteg", "zsteg", "stego", "PNG/BMP steganography analysis"),
    KaliTool("apktool", "apktool", "mobile", "Android package analysis"),
    KaliTool("jadx", "jadx", "mobile", "Android decompilation"),
    KaliTool("adb", "adb", "mobile", "Android device interaction"),
)


def get_kali_tool(name: str) -> KaliTool | None:
    return next((tool for tool in KALI_TOOLS if tool.name == name), None)


def list_kali_tools(category: str | None = None) -> tuple[KaliTool, ...]:
    if category is None:
        return KALI_TOOLS
    return tuple(tool for tool in KALI_TOOLS if tool.category == category)
