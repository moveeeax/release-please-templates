# Python package template

`release-type: python` keeps the version in `pyproject.toml`
(`[project] version`) and/or `<pkg>/__init__.py` `__version__` in sync with the
release tag, and maintains `CHANGELOG.md`.

After the release PR merges, wire your publish step to the created tag:

```yaml
on:
  push:
    tags: ["v*"]
```
