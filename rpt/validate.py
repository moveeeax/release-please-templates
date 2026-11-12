"""Validate the release-please config and manifest files.

``validate_config`` first checks the config against the official
release-please JSON schema (see ``schema.py``), then the invariants the schema
does not express: every package needs a known ``release-type``, multi-package
configs need unique components, and changelog sections must be well formed.
``validate_manifest`` checks that every manifest key has a matching package and
a valid semver.
"""
from __future__ import annotations

from .bump import parse_version
from .schema import validate_schema

VALID_RELEASE_TYPES = {
    "go", "python", "simple", "terraform-module", "node", "rust", "helm", "maven",
}


class ValidationError(Exception):
    pass


def validate_config(config: dict, schema: dict | None = None) -> list[str]:
    """Return config errors. ``schema`` defaults to the vendored copy."""
    errors = validate_schema(config, schema)
    if not isinstance(config, dict):
        return errors
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

    # The vendored schema already requires both keys; this covers a custom
    # --schema-url that does not, without reporting the same problem twice.
    schema_saw_sections = any(e.startswith("config['changelog-sections']") for e in errors)
    for i, sec in enumerate(config.get("changelog-sections", [])):
        if schema_saw_sections:
            break
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
