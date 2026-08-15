# Go module template

Drop `.github/workflows/release-please.yml`, `release-please-config.json` and
`.release-please-manifest.json` into the root of a Go module.

* `release-type: go` writes the version into a `version.go` / release notes and
  tags `vX.Y.Z` — the tag form Go modules require.
* Pre-1.0 is friendly: a breaking change bumps the minor, a `feat` bumps the
  patch, so you do not jump to `v1.0.0` by accident while the API is unstable.

Seed `.release-please-manifest.json` with the version already released (or
`0.0.0` for a fresh module) and let the release PR take it from there.
