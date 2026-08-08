from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ToolProfile:
    name: str
    specialist: str
    commands: tuple[str, ...]


PROFILES: tuple[ToolProfile, ...] = (
    ToolProfile("web", "web", ("curl", "wget", "nmap", "ffuf", "gobuster", "feroxbuster", "dirsearch", "nikto", "sqlmap", "whatweb")),
    ToolProfile("crypto", "crypto", ("openssl", "gpg", "hashid", "hashcat", "john", "strings", "xxd")),
    ToolProfile("forensics", "forensics", ("file", "exiftool", "binwalk", "foremost", "scalpel", "strings", "xxd")),
    ToolProfile("stego", "stego", ("zsteg", "steghide", "stegseek", "pngcheck", "exiftool")),
    ToolProfile("reverse", "reverse", ("ghidra", "radare2", "rizin", "objdump", "readelf", "nm", "strings", "gdb")),
    ToolProfile("pwn", "pwn", ("gdb", "checksec", "python", "ropper", "readelf", "objdump", "patchelf")),
    ToolProfile("network", "network", ("nmap", "masscan", "rustscan", "tcpdump", "tshark", "dig", "nslookup", "whois")),
    ToolProfile("osint", "osint", ("amass", "subfinder", "theHarvester", "dnsrecon", "whois", "dig", "curl")),
    ToolProfile("mobile", "mobile", ("adb", "apktool", "jadx", "aapt", "apksigner")),
    ToolProfile("blockchain", "blockchain", ("curl", "python", "jq", "openssl")),
    ToolProfile("misc", "misc", ("python", "bash", "file", "strings", "xxd", "jq", "git")),
)


def profile_for_specialist(name: str) -> ToolProfile | None:
    return next((profile for profile in PROFILES if profile.specialist == name), None)
