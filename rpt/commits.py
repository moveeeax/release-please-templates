"""Parse Conventional Commits (https://www.conventionalcommits.org/).

We only need the pieces that drive a release: the type, an optional scope, the
breaking-change marker (``!`` in the header or a ``BREAKING CHANGE:`` footer),
and the subject line.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# type(scope)!: subject   — scope and the ! are optional.
_HEADER = re.compile(
    r"^(?P<type>[a-zA-Z]+)"
    r"(?:\((?P<scope>[^)]*)\))?"
    r"(?P<bang>!)?:\s+(?P<subject>.+)$"
)
_BREAKING_FOOTER = re.compile(r"^BREAKING[ -]CHANGE:\s*.+", re.IGNORECASE)


@dataclass(frozen=True)
class Commit:
    type: str
    subject: str
    scope: str | None = None
    breaking: bool = False
    header: str = ""

    @property
    def scoped(self) -> str:
        return f"{self.type}({self.scope})" if self.scope else self.type


def parse_commit(message: str) -> Commit | None:
    """Parse one commit message. Returns ``None`` if the header is not a valid
    conventional-commit header (release-please ignores such commits)."""
    lines = message.strip("\n").splitlines()
    if not lines:
        return None
    header = lines[0].strip()
    m = _HEADER.match(header)
    if not m:
        return None
    breaking = bool(m.group("bang")) or any(
        _BREAKING_FOOTER.match(l.strip()) for l in lines[1:]
    )
    return Commit(
        type=m.group("type").lower(),
        scope=m.group("scope"),
        subject=m.group("subject").strip(),
        breaking=breaking,
        header=header,
    )


def parse_commits(text: str) -> list[Commit]:
    """Parse a newline-separated list of single-line commit headers.

    Blank lines are skipped; non-conforming lines are dropped (as release-please
    would ignore them for versioning)."""
    out: list[Commit] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        c = parse_commit(line)
        if c is not None:
            out.append(c)
    return out
