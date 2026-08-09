import json

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.plugins.discovery import PluginDiscoveryError, discover_manifests, load_manifest
from app.plugins.signing import create_manifest, verify_manifest


def test_signed_manifest_verifies() -> None:
    private_key = Ed25519PrivateKey.generate()
    manifest = create_manifest(
        private_key,
        name="web-specialist",
        version="1.2.0",
        api_version="1",
        capabilities=("http.fetch", "http.enumerate"),
        publisher="ctf-os-core",
    )

    assert verify_manifest(manifest)
    assert manifest.capabilities == ("http.enumerate", "http.fetch")


def test_tampered_manifest_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    manifest = create_manifest(
        private_key,
        name="crypto-specialist",
        version="1.0.0",
        api_version="1",
        capabilities=("crypto.analyze",),
        publisher="ctf-os-core",
    )
    manifest = type(manifest)(
        name=manifest.name,
        version="9.9.9",
        api_version=manifest.api_version,
        capabilities=manifest.capabilities,
        publisher=manifest.publisher,
        public_key=manifest.public_key,
        signature=manifest.signature,
    )

    assert not verify_manifest(manifest)


def test_discovery_requires_a_valid_signature(tmp_path) -> None:
    private_key = Ed25519PrivateKey.generate()
    manifest = create_manifest(
        private_key,
        name="forensics-specialist",
        version="1.0.0",
        api_version="1",
        capabilities=("file.hash",),
        publisher="ctf-os-core",
    )
    plugin_dir = tmp_path / "forensics"
    plugin_dir.mkdir()
    (plugin_dir / "plugin.json").write_text(json.dumps(manifest.as_dict()), encoding="utf-8")

    discovered = discover_manifests(tmp_path)
    assert discovered == (manifest,)

    manifest_dict = manifest.as_dict()
    manifest_dict["publisher"] = "attacker"
    (plugin_dir / "plugin.json").write_text(json.dumps(manifest_dict), encoding="utf-8")

    with pytest.raises(PluginDiscoveryError):
        load_manifest(plugin_dir / "plugin.json")
