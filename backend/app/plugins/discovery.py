from __future__ import annotations

import json
from pathlib import Path

from app.plugins.signing import PluginManifest, verify_manifest


class PluginDiscoveryError(ValueError):
    pass


def load_manifest(path: Path) -> PluginManifest:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        manifest = PluginManifest(
            name=str(raw["name"]),
            version=str(raw["version"]),
            api_version=str(raw["api_version"]),
            capabilities=tuple(str(item) for item in raw["capabilities"]),
            publisher=str(raw["publisher"]),
            public_key=str(raw["public_key"]),
            signature=str(raw["signature"]),
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise PluginDiscoveryError(f"invalid plugin manifest: {path}") from exc

    if not manifest.name or not manifest.version or not manifest.api_version:
        raise PluginDiscoveryError(f"plugin manifest has missing identity fields: {path}")
    if not manifest.capabilities:
        raise PluginDiscoveryError(f"plugin manifest declares no capabilities: {path}")
    if not verify_manifest(manifest):
        raise PluginDiscoveryError(f"plugin manifest signature verification failed: {path}")
    return manifest


def discover_manifests(root: Path) -> tuple[PluginManifest, ...]:
    if not root.exists():
        return ()
    manifests = [load_manifest(path) for path in sorted(root.rglob("plugin.json"))]
    return tuple(manifests)
