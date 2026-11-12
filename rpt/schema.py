"""JSON-schema check against the official release-please config schema.

``schemas/config.json`` is a verbatim copy of
https://github.com/googleapis/release-please/blob/main/schemas/config.json
taken at commit ``VENDORED_SCHEMA_COMMIT``. ``load_schema`` can read another
copy from a URL or a local path instead (``rpt validate --schema-url``).

Two additions on top of plain schema validation:

* unknown keys get a ``did you mean`` hint from the schema's property names;
* package entries are checked for unknown keys too. The upstream schema allows
  any key under ``packages.<path>``, so a typo there would otherwise pass. The
  allowed set is ``ReleaserConfigOptions`` plus the package-only keys from
  ``ReleaserPackageConfig``/``ReleaserConfigJson`` in release-please's
  ``src/manifest.ts``.
"""
from __future__ import annotations

import difflib
import json
import os
import urllib.request
from importlib import resources

from jsonschema import Draft7Validator
from jsonschema.exceptions import best_match

VENDORED_SCHEMA_COMMIT = "fa67225b42d8133331a1b48e89640b60e9ca6a23"

# Keys release-please reads from a package entry that ReleaserConfigOptions in
# schemas/config.json does not list (src/manifest.ts, ReleaserPackageConfig and
# ReleaserConfigJson).
PACKAGE_ONLY_KEYS = {"package-name", "component", "label", "release-label"}

FETCH_TIMEOUT = 10


class SchemaLoadError(Exception):
    pass


def load_schema(source: str | None = None) -> dict:
    """Return the vendored schema, or the one at ``source`` (URL or path)."""
    try:
        if source is None:
            text = resources.files("rpt").joinpath("schemas/config.json").read_text()
        elif "://" in source:
            with urllib.request.urlopen(source, timeout=FETCH_TIMEOUT) as resp:
                text = resp.read().decode("utf-8")
        else:
            with open(os.path.expanduser(source)) as f:
                text = f.read()
        schema = json.loads(text)
    except (OSError, ValueError) as e:
        raise SchemaLoadError(f"cannot load schema from {source or 'vendored copy'}: {e}") from e
    if not isinstance(schema, dict):
        raise SchemaLoadError(f"schema from {source} is not a JSON object")
    return schema


def _where(path) -> str:
    out = "config"
    for part in path:
        out += f"[{part}]" if isinstance(part, int) else f"[{part!r}]"
    return out


def _unknown_keys(where: str, keys, known) -> list[str]:
    known = sorted(known)
    errors = []
    for key in sorted(keys):
        if key in known:
            continue
        msg = f"{where}: unknown key {key!r}"
        match = difflib.get_close_matches(key, known, n=1)
        if match:
            msg += f" (did you mean {match[0]!r}?)"
        errors.append(msg)
    return errors


def _any_of_detail(err) -> str:
    """Explain an anyOf/oneOf failure (extra-files, plugins entries).

    A branch whose root type or ``type`` discriminator does not match the
    entry is not what the author meant; if exactly one branch is left, its
    errors are the useful ones (e.g. a json extra-file missing ``jsonpath``).
    """
    branches: dict = {}
    for sub in err.context:
        branches.setdefault(sub.relative_schema_path[0], []).append(sub)

    def mismatched(subs) -> bool:
        return any(
            (sub.validator == "type" and not sub.relative_path)
            or (sub.validator == "enum" and list(sub.relative_path) == ["type"])
            for sub in subs
        )

    left = [subs for subs in branches.values() if not mismatched(subs)]
    if len(left) == 1:
        return "; ".join(sub.message for sub in left[0])
    return best_match(err.context).message


def validate_schema(config, schema: dict | None = None) -> list[str]:
    """Validate ``config`` against the release-please schema.

    Returns human-readable errors, empty when the config conforms.
    """
    if schema is None:
        schema = load_schema()
    errors: list[str] = []
    validator = Draft7Validator(schema)
    for err in sorted(validator.iter_errors(config), key=lambda e: list(map(str, e.absolute_path))):
        where = _where(err.absolute_path)
        if err.validator == "additionalProperties" and isinstance(err.instance, dict):
            known = set(err.schema.get("properties", {}))
            errors += _unknown_keys(where, set(err.instance) - known, known)
        elif err.context:
            errors.append(f"{where}: {_any_of_detail(err)}")
        else:
            errors.append(f"{where}: {err.message}")

    pkg_props = schema.get("definitions", {}).get("ReleaserConfigOptions", {}).get("properties")
    packages = config.get("packages") if isinstance(config, dict) else None
    if pkg_props and isinstance(packages, dict):
        known = set(pkg_props) | PACKAGE_ONLY_KEYS
        for path, pkg in packages.items():
            if isinstance(pkg, dict):
                errors += _unknown_keys(_where(["packages", path]), pkg, known)
    # The schema repeats its rules at the top level and under allOf, so the
    # same failure can come back twice.
    return list(dict.fromkeys(errors))
