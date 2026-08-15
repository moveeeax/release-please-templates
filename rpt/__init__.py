"""rpt — release-please template toolkit.

A tiny, dependency-light library that (1) validates the release-please config
and manifest files shipped in ``templates/`` and (2) simulates the version bump
and changelog that release-please would produce for a set of conventional
commits. The simulator is what lets the templates be unit-tested: given a
config and a list of commits, we assert the resulting version and changelog.
"""
from .commits import Commit, parse_commit, parse_commits
from .bump import (
    LEVEL_NONE, LEVEL_PATCH, LEVEL_MINOR, LEVEL_MAJOR,
    commit_level, release_level, next_version, changelog, simulate,
)
from .validate import validate_config, validate_manifest, ValidationError

__all__ = [
    "Commit", "parse_commit", "parse_commits",
    "LEVEL_NONE", "LEVEL_PATCH", "LEVEL_MINOR", "LEVEL_MAJOR",
    "commit_level", "release_level", "next_version", "changelog", "simulate",
    "validate_config", "validate_manifest", "ValidationError",
]

__version__ = "0.1.0"
