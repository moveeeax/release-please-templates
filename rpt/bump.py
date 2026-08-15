"""Simulate the release-please version bump and changelog.

The bump rules mirror release-please defaults:

* a breaking change  -> major
* ``feat``           -> minor
* ``fix``            -> patch
* anything else      -> no release on its own (but still shown in the changelog
  if a release is triggered and its type has a visible section)

Pre-1.0 behaviour is controlled by two config options that release-please also
exposes: ``bump-minor-pre-major`` (breaking -> minor while 0.x) and
``bump-patch-for-minor-pre-major`` (feat -> patch while 0.x).
"""
from __future__ import annotations

from .commits import Commit

LEVEL_NONE, LEVEL_PATCH, LEVEL_MINOR, LEVEL_MAJOR = 0, 1, 2, 3

# release-please default sections when a config omits changelog-sections.
DEFAULT_SECTIONS = [
    {"type": "feat", "section": "Features"},
    {"type": "fix", "section": "Bug Fixes"},
]


def parse_version(v: str) -> tuple[int, int, int]:
    v = v.strip().lstrip("v")
    parts = (v.split("-", 1)[0]).split(".")
    if len(parts) < 3:
        raise ValueError(f"not a semver: {v!r}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def commit_level(c: Commit) -> int:
    if c.breaking:
        return LEVEL_MAJOR
    if c.type == "feat":
        return LEVEL_MINOR
    if c.type == "fix":
        return LEVEL_PATCH
    return LEVEL_NONE


def release_level(commits: list[Commit]) -> int:
    return max((commit_level(c) for c in commits), default=LEVEL_NONE)


def next_version(current: str, level: int, options: dict | None = None) -> str | None:
    """Compute the next version string, or ``None`` when nothing releasable."""
    if level == LEVEL_NONE:
        return None
    options = options or {}
    major, minor, patch = parse_version(current)
    eff = level
    if major == 0:
        if level == LEVEL_MAJOR and options.get("bump-minor-pre-major"):
            eff = LEVEL_MINOR
        elif level == LEVEL_MINOR and options.get("bump-patch-for-minor-pre-major"):
            eff = LEVEL_PATCH
    if eff == LEVEL_MAJOR:
        return f"{major + 1}.0.0"
    if eff == LEVEL_MINOR:
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def changelog(commits: list[Commit], sections: list[dict] | None = None) -> list[dict]:
    """Group commits into changelog sections, in the section order given by the
    config, skipping hidden sections and empty groups."""
    sections = sections or DEFAULT_SECTIONS
    visible = [s for s in sections if not s.get("hidden")]
    label = {s["type"]: s["section"] for s in visible}
    groups: dict[str, list[Commit]] = {s["type"]: [] for s in visible}
    for c in commits:
        if c.type in groups:
            groups[c.type].append(c)
    out = []
    for s in visible:
        t = s["type"]
        if groups[t]:
            out.append({"type": t, "section": label[t], "commits": groups[t]})
    return out


def render_changelog(version: str, groups: list[dict], breaking: list[Commit] | None = None) -> str:
    lines = [f"## {version}", ""]
    if breaking:
        lines.append("### ⚠ BREAKING CHANGES")
        lines.append("")
        for c in breaking:
            lines.append(f"* {c.subject}")
        lines.append("")
    for g in groups:
        lines.append(f"### {g['section']}")
        lines.append("")
        for c in g["commits"]:
            scope = f"**{c.scope}:** " if c.scope else ""
            lines.append(f"* {scope}{c.subject}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def simulate(config: dict, current: str, commits: list[Commit]) -> dict:
    """Tie it together: given a release-please config dict, the current version
    and the commits since that version, return the release decision."""
    options = {k: config[k] for k in ("bump-minor-pre-major", "bump-patch-for-minor-pre-major") if k in config}
    level = release_level(commits)
    version = next_version(current, level, options)
    groups = changelog(commits, config.get("changelog-sections"))
    breaking = [c for c in commits if c.breaking]
    return {
        "release": version is not None,
        "current_version": current,
        "next_version": version,
        "level": level,
        "changelog": groups,
        "changelog_md": render_changelog(version, groups, breaking) if version else "",
    }
