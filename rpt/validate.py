"""Validate the release-please config and manifest files.

Not a full JSON-schema check — just the invariants that break real setups:
every package needs a ``release-type``, every manifest key must have a matching
package and a valid semver, and changelog sections must be well formed.
"""
from __future__ import annotations

from .bump import parse_version

VALID_RELEASE_TYPES = {
    "go", "python", "simple", "terraform-module", "node", "rust", "helm", "maven",
}


class ValidationError(Exception):
    pass


def validate_config(config: dict) -> list[str]:
    errors: list[str] = []
    packages = config.get("packages")
    if not isinstance(packages, dict) or not packages:
        errors.append("config.packages must be a non-empty object")
        packages = packages if isinstance(packages, dict) else {}

    for path, pkg in packages.items():
        rt = pkg.get("release-type") or config.get("release-type")
        if not rt:
            errors.append(f"package {path!r}: missing release-type")
        elif rt not in VALID_RELEASE_TYPES:
            errors.append(f"package {path!r}: unknown release-type {rt!r}")

    if len(packages) > 1:
        components = [p.get("component") for p in packages.values()]
        if any(c is None for c in components):
            errors.append("multi-package config: every package needs a 'component'")
        elif len(set(components)) != len(components):
            errors.append("multi-package config: duplicate 'component' names")

    for i, sec in enumerate(config.get("changelog-sections", [])):
        if "type" not in sec or "section" not in sec:
            errors.append(f"changelog-sections[{i}]: needs both 'type' and 'section'")
    return errors


def validate_manifest(config: dict, manifest: dict) -> list[str]:
    errors: list[str] = []
    packages = config.get("packages", {})
    for path in packages:
        if path not in manifest:
            errors.append(f"manifest missing version for package {path!r}")
    for path, version in manifest.items():
        if path not in packages:
            errors.append(f"manifest has {path!r} not present in config.packages")
        try:
            parse_version(str(version))
        except ValueError:
            errors.append(f"manifest[{path!r}]: {version!r} is not a semver")
    return errors
