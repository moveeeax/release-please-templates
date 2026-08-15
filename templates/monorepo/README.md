# Monorepo template (manifest mode)

One release-please config, many packages. Each entry in `packages` gets its own
version (tracked in `.release-please-manifest.json`), its own release PR
(`separate-pull-requests: true`) and its own tag via `component`:
`api-v1.2.0`, `cli-v0.4.1`, `pylib-v0.9.0`.

release-please decides which packages to bump from the *paths* touched by each
commit, so a `feat` under `packages/cli/**` only bumps `cli`. Add a package by
adding a `packages` entry **and** a matching `.release-please-manifest.json`
key — `python -m rpt validate` (and the CI here) fails if either is missing.
