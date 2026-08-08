from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SpecialistDefinition:
    name: str
    category: str
    description: str
    capabilities: tuple[str, ...]


SPECIALISTS: tuple[SpecialistDefinition, ...] = (
    SpecialistDefinition("crypto", "cryptography", "Encoding, hashes, classical ciphers and cryptanalysis.", ("crypto.detect", "crypto.decode", "crypto.analyze")),
    SpecialistDefinition("web", "web", "Web challenge discovery and application analysis.", ("web.inspect", "web.enumerate", "web.analyze")),
    SpecialistDefinition("forensics", "forensics", "Artifact, file and digital-forensics analysis.", ("forensics.identify", "forensics.extract", "forensics.analyze")),
    SpecialistDefinition("reverse", "reverse", "Static and dynamic binary analysis.", ("reverse.identify", "reverse.strings", "reverse.analyze")),
    SpecialistDefinition("pwn", "pwn", "Binary exploitation challenge analysis in isolated labs.", ("pwn.identify", "pwn.analyze", "pwn.test")),
    SpecialistDefinition("network", "network", "Packet captures, protocols and network artifacts.", ("network.identify", "network.extract", "network.analyze")),
    SpecialistDefinition("stego", "steganography", "Hidden-data and media steganography analysis.", ("stego.identify", "stego.extract", "stego.analyze")),
    SpecialistDefinition("osint", "osint", "Open-source intelligence challenge analysis.", ("osint.collect", "osint.correlate", "osint.analyze")),
    SpecialistDefinition("mobile", "mobile", "Android and mobile challenge analysis.", ("mobile.identify", "mobile.extract", "mobile.analyze")),
    SpecialistDefinition("blockchain", "blockchain", "Smart-contract and blockchain challenge analysis.", ("blockchain.inspect", "blockchain.trace", "blockchain.analyze")),
    SpecialistDefinition("misc", "misc", "General puzzle, encoding and challenge glue logic.", ("misc.identify", "misc.transform", "misc.analyze")),
)


def get_specialist(name: str) -> SpecialistDefinition | None:
    return next((item for item in SPECIALISTS if item.name == name), None)
