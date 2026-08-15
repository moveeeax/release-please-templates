# Monorepo manifest demo

A worked example the test-suite checks (`tests/test_templates.py`). Given the
starting versions in `.release-please-manifest.json` and the commits in
`expected.json`, release-please would cut:

| package        | from   | commits                              | to      |
|----------------|--------|--------------------------------------|---------|
| `packages/api` | 1.2.0  | `feat(api):` + `fix(api):`           | 1.3.0   |
| `packages/cli` | 0.4.1  | `fix(cli):`                          | 0.4.2   |
| `libs/pylib`   | 0.9.0  | `feat(pylib)!:` (breaking, pre-1.0)  | 0.10.0  |

Note `pylib`: a breaking change on a `0.x` package bumps the *minor*, not the
major, because `bump-minor-pre-major` is on.

Reproduce any row locally:

```console
$ printf 'feat(api): add pagination\nfix(api): handle nil\n' > /tmp/c.txt
$ python -m rpt simulate --config examples/monorepo-manifest-demo/release-please-config.json \
    --current 1.2.0 --commits /tmp/c.txt
1.2.0 -> 1.3.0
```
