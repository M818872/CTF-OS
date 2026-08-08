from __future__ import annotations

import shutil
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KaliTool:
    name: str
    category: str
    description: str
    binary: str | None = None
    package: str | None = None


# High-value Kali/security tooling. Runtime discovery supplements this list so
# CTF-OS does not need to hard-code every package shipped by every Kali release.
KALI_TOOLS: tuple[KaliTool, ...] = (
    KaliTool("nmap", "network", "Network discovery and service enumeration", "nmap", "nmap"),
    KaliTool("masscan", "network", "High-speed TCP port scanning", "masscan", "masscan"),
    KaliTool("rustscan", "network", "Fast port discovery and service enumeration", "rustscan", "rustscan"),
    KaliTool("tcpdump", "network", "Packet capture and inspection", "tcpdump", "tcpdump"),
    KaliTool("tshark", "network", "Command-line Wireshark packet analysis", "tshark", "tshark"),
    KaliTool("wireshark", "network", "Graphical packet analysis", "wireshark", "wireshark"),
    KaliTool("nikto", "web", "Web server assessment", "nikto", "nikto"),
    KaliTool("gobuster", "web", "Content and DNS enumeration", "gobuster", "gobuster"),
    KaliTool("ffuf", "web", "Fast web fuzzing", "ffuf", "ffuf"),
    KaliTool("feroxbuster", "web", "Web content discovery", "feroxbuster", "feroxbuster"),
    KaliTool("dirsearch", "web", "Web path discovery", "dirsearch", "dirsearch"),
    KaliTool("sqlmap", "web", "SQL injection testing", "sqlmap", "sqlmap"),
    KaliTool("whatweb", "web", "Web technology fingerprinting", "whatweb", "whatweb"),
    KaliTool("curl", "web", "HTTP client", "curl", "curl"),
    KaliTool("wget", "web", "HTTP/file retrieval", "wget", "wget"),
    KaliTool("burpsuite", "web", "Web security testing platform", "burpsuite", "burpsuite"),
    KaliTool("john", "crypto", "Password hash auditing", "john", "john"),
    KaliTool("hashcat", "crypto", "Password recovery and hash auditing", "hashcat", "hashcat"),
    KaliTool("hashid", "crypto", "Hash identification", "hashid", "hashid"),
    KaliTool("hash-identifier", "crypto", "Hash identification", "hash-identifier", "hash-identifier"),
    KaliTool("openssl", "crypto", "Cryptographic operations and certificates", "openssl", "openssl"),
    KaliTool("gpg", "crypto", "OpenPGP operations", "gpg", "gnupg"),
    KaliTool("exiftool", "forensics", "Metadata extraction", "exiftool", "libimage-exiftool-perl"),
    KaliTool("binwalk", "forensics", "Firmware and embedded-file analysis", "binwalk", "binwalk"),
    KaliTool("file", "forensics", "File type identification", "file", "file"),
    KaliTool("strings", "forensics", "Printable string extraction", "strings", "binutils"),
    KaliTool("xxd", "forensics", "Hex dump and conversion", "xxd", "vim-common"),
    KaliTool("foremost", "forensics", "File carving", "foremost", "foremost"),
    KaliTool("scalpel", "forensics", "File carving", "scalpel", "scalpel"),
    KaliTool("zsteg", "stego", "PNG/BMP steganography analysis", "zsteg", "zsteg"),
    KaliTool("steghide", "stego", "Steganography extraction and embedding", "steghide", "steghide"),
    KaliTool("stegseek", "stego", "Steghide password recovery", "stegseek", "stegseek"),
    KaliTool("pngcheck", "stego", "PNG structure validation", "pngcheck", "pngcheck"),
    KaliTool("gdb", "pwn", "GNU debugger", "gdb", "gdb"),
    KaliTool("gdb-multiarch", "pwn", "Multi-architecture debugger", "gdb-multiarch", "gdb-multiarch"),
    KaliTool("pwntools", "pwn", "Python exploitation framework", "pwn", "python3-pwntools"),
    KaliTool("checksec", "pwn", "Binary security property inspection", "checksec", "checksec"),
    KaliTool("patchelf", "pwn", "ELF modification and inspection", "patchelf", "patchelf"),
    KaliTool("ropper", "pwn", "ROP gadget discovery", "ropper", "ropper"),
    KaliTool("radare2", "reverse", "Reverse engineering framework", "r2", "radare2"),
    KaliTool("rizin", "reverse", "Reverse engineering framework", "rz", "rizin"),
    KaliTool("objdump", "reverse", "Binary disassembly and inspection", "objdump", "binutils"),
    KaliTool("readelf", "reverse", "ELF inspection", "readelf", "binutils"),
    KaliTool("nm", "reverse", "Symbol inspection", "nm", "binutils"),
    KaliTool("apktool", "mobile", "Android APK reverse engineering", "apktool", "apktool"),
    KaliTool("jadx", "mobile", "Android DEX decompilation", "jadx", "jadx"),
    KaliTool("adb", "mobile", "Android device bridge", "adb", "adb"),
    KaliTool("amass", "osint", "Attack-surface and DNS enumeration", "amass", "amass"),
    KaliTool("theHarvester", "osint", "OSINT collection", "theHarvester", "theharvester"),
    KaliTool("subfinder", "osint", "Subdomain discovery", "subfinder", "subfinder"),
    KaliTool("dnsrecon", "osint", "DNS enumeration", "dnsrecon", "dnsrecon"),
    KaliTool("whois", "osint", "WHOIS lookup", "whois", "whois"),
    KaliTool("git", "misc", "Repository and source inspection", "git", "git"),
    KaliTool("python3", "misc", "Python runtime for analysis scripts", "python3", "python3"),
    KaliTool("jq", "misc", "JSON processing", "jq", "jq"),
    KaliTool("unzip", "misc", "ZIP archive extraction", "unzip", "unzip"),
    KaliTool("7z", "misc", "Archive inspection and extraction", "7z", "7zip"),
)


def installed_tools() -> tuple[KaliTool, ...]:
    """Return catalogued tools available in the current execution environment."""
    return tuple(tool for tool in KALI_TOOLS if tool.binary and shutil.which(tool.binary))


def discover_commands() -> tuple[str, ...]:
    """Discover executable commands from PATH without executing them."""
    paths: set[str] = set()
    for directory in __import__("os").environ.get("PATH", "").split(__import__("os").pathsep):
        if not directory:
            continue
        try:
            for entry in __import__("os").listdir(directory):
                full = __import__("os").path.join(directory, entry)
                if __import__("os").path.isfile(full) and __import__("os").access(full, __import__("os").X_OK):
                    paths.add(entry)
        except OSError:
            continue
    return tuple(sorted(paths))
