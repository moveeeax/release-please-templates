# release-please-templates

[![ci](https://github.com/moveeeax/release-please-templates/actions/workflows/ci.yml/badge.svg)](https://github.com/moveeeax/release-please-templates/actions/workflows/ci.yml)
[![python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> Automated releases and changelogs, preconfigured per language.

Copy-paste [release-please](https://github.com/googleapis/release-please) setups
for Go, Python, Terraform modules and manifest-driven monorepos — plus a tiny
toolkit that **validates** each config and **simulates** the version bump so the
templates are actually tested, not just hopefully-correct YAML.

## What's in the box

```
templates/
  go/                 release-type: go
  python/             release-type: python
  terraform-module/   release-type: terraform-module
  monorepo/           manifest mode, three packages, per-component tags
examples/
  monorepo-manifest-demo/   a worked bump the tests assert
docs/
  commit-conventions.md     which commit type bumps what
  pr-flow.md                how the release PR actually works
rpt/                  the validate + simulate library (this repo's CI target)
```

Each template ships three files to drop into a repo root:
`.github/workflows/release-please.yml`, `release-please-config.json` and
`.release-please-manifest.json`.

## Quick start

Pick a template and copy it into your project:

```console
$ cp -r templates/go/. /path/to/your/module/
$ git add .github release-please-config.json .release-please-manifest.json
$ git commit -m "ci: add release-please"
```

Set the current version in `.release-please-manifest.json` (use `0.0.0` for a
fresh project), push to `main`, and release-please opens a release PR. Merge it
to tag and publish. The full flow is in [docs/pr-flow.md](docs/pr-flow.md).

## The toolkit (`rpt`)

Install locally and validate or simulate any config:

```console
$ pip install -e .[test]
$ python -m rpt validate templates/monorepo/release-please-config.json \
    templates/monorepo/.release-please-manifest.json
ok: templates/monorepo/release-please-config.json is a valid release-please config

$ printf 'feat: add --keep-last\nfix: off-by-one\n' > /tmp/c.txt
$ python -m rpt simulate --config templates/go/release-please-config.json \
    --current 0.3.0 --commits /tmp/c.txt
0.3.0 -> 0.3.1

### Features
* add --keep-last

### Bug Fixes
* off-by-one
```

The bump rules mirror release-please: `fix` → patch, `feat` → minor, breaking →
major, with the pre-1.0 softening (`bump-minor-pre-major`,
`bump-patch-for-minor-pre-major`) the templates enable by default.

## How it works

`rpt` parses conventional-commit headers, maps them to a bump level, applies the
pre-1.0 options, and groups commits into changelog sections in config order.
`tests/test_templates.py` loads every template and the monorepo demo and asserts
both the validation passes and the simulated versions match a checked-in
`expected.json` — so a broken template fails CI instead of your next release.

## Develop

```console
$ python3 -m venv .venv && . .venv/bin/activate
$ pip install -e .[test]
$ pytest -q
```

## License

MIT — see [LICENSE](LICENSE).
