"""Small CLI: validate a template or simulate a release.

    python -m rpt validate templates/go/release-please-config.json \
        templates/go/.release-please-manifest.json
    python -m rpt simulate --config templates/go/release-please-config.json \
        --current 1.4.0 --commits commits.txt
"""
from __future__ import annotations

import argparse
import json
import sys

from .commits import parse_commits
from .validate import validate_config, validate_manifest
from .bump import simulate


def _load(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def cmd_validate(args) -> int:
    config = _load(args.config)
    errors = validate_config(config)
    if args.manifest:
        errors += validate_manifest(config, _load(args.manifest))
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"ok: {args.config} is a valid release-please config")
    return 0


def cmd_simulate(args) -> int:
    config = _load(args.config)
    with open(args.commits) as f:
        commits = parse_commits(f.read())
    result = simulate(config, args.current, commits)
    if args.json:
        printable = dict(result)
        printable["changelog"] = [
            {"section": g["section"], "commits": [c.header for c in g["commits"]]}
            for g in result["changelog"]
        ]
        print(json.dumps(printable, indent=2))
    else:
        if result["release"]:
            print(f"{args.current} -> {result['next_version']}")
            print()
            print(result["changelog_md"], end="")
        else:
            print("no release: no feat/fix/breaking commits since last release")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="rpt", description="release-please template toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="validate a release-please config/manifest")
    v.add_argument("config")
    v.add_argument("manifest", nargs="?")
    v.set_defaults(func=cmd_validate)

    s = sub.add_parser("simulate", help="simulate a release from commits")
    s.add_argument("--config", required=True)
    s.add_argument("--current", required=True, help="current version, e.g. 1.2.0")
    s.add_argument("--commits", required=True, help="file of one commit header per line")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_simulate)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
