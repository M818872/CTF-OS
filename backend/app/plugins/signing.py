from __future__ import annotations

import base64
import json
from dataclasses import dataclass, replace
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


@dataclass(frozen=True, slots=True)
class PluginManifest:
    name: str
    version: str
    api_version: str
    capabilities: tuple[str, ...]
    publisher: str
    public_key: str
    signature: str

    def unsigned_payload(self) -> bytes:
        payload = {
            "api_version": self.api_version,
            "capabilities": list(self.capabilities),
            "name": self.name,
            "publisher": self.publisher,
            "version": self.version,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    def as_dict(self) -> dict[str, Any]:
        return {
            "api_version": self.api_version,
            "capabilities": list(self.capabilities),
            "name": self.name,
            "publisher": self.publisher,
            "version": self.version,
            "public_key": self.public_key,
            "signature": self.signature,
        }


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_manifest(
    private_key: Ed25519PrivateKey,
    *,
    name: str,
    version: str,
    api_version: str,
    capabilities: tuple[str, ...],
    publisher: str,
) -> PluginManifest:
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    manifest = PluginManifest(
        name=name,
        version=version,
        api_version=api_version,
        capabilities=tuple(sorted(set(capabilities))),
        publisher=publisher,
        public_key=_b64(public_key),
        signature="",
    )
    return replace(manifest, signature=_b64(private_key.sign(manifest.unsigned_payload())))


def verify_manifest(manifest: PluginManifest) -> bool:
    try:
        key = Ed25519PublicKey.from_public_bytes(_unb64(manifest.public_key))
        key.verify(_unb64(manifest.signature), manifest.unsigned_payload())
        return True
    except (InvalidSignature, ValueError):
        return False
