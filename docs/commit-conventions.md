# Commit conventions

These templates read [Conventional Commits](https://www.conventionalcommits.org/).
The commit *type* decides the version bump and where the message shows up in the
changelog.

## Types that trigger a release

| Commit                     | Bump (>= 1.0)        | Changelog section |
|----------------------------|----------------------|-------------------|
| `fix: ...`                 | patch                | Bug Fixes         |
| `feat: ...`                | minor                | Features          |
| `feat!: ...` / footer      | major                | ⚠ Breaking Changes |

A breaking change is either a `!` after the type/scope (`feat!:`, `fix(api)!:`)
or a `BREAKING CHANGE:` footer in the body.

## Pre-1.0 behaviour

While a package is on `0.x` these templates set `bump-minor-pre-major` and
`bump-patch-for-minor-pre-major`, so:

* a breaking change bumps the **minor** (`0.3.0 -> 0.4.0`)
* a `feat` bumps the **patch** (`0.3.0 -> 0.3.1`)

That keeps you from lurching to `v1.0.0` before the API has settled.

## Types that only show in the changelog

`perf`, `deps`, `revert` appear under their own headings *if* a release is cut,
but do not trigger one on their own. `docs`, `style`, `chore`, `refactor`,
`test`, `build`, `ci` are hidden.

## Try it

```console
$ printf 'feat: add --keep-last\nfix: off-by-one in retention\n' > /tmp/c.txt
$ python -m rpt simulate --config templates/go/release-please-config.json \
    --current 0.3.0 --commits /tmp/c.txt
0.3.0 -> 0.3.1
```
