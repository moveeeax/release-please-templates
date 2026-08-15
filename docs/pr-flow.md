# The release PR flow

release-please does not release on every push. It maintains a long-lived
**release PR** and only tags when you merge it.

1. You merge conventional commits into `main`.
2. The `release-please` workflow opens (or updates) a release PR titled
   `chore(main): release <version>`. The PR body is the changelog it will
   publish, and `.release-please-manifest.json` is updated inside the PR.
3. Review the proposed version + changelog. Keep merging feature PRs — the
   release PR keeps rebasing itself.
4. When you merge the release PR, release-please tags `vX.Y.Z`, creates the
   GitHub Release, and (in monorepo mode) does this per component.

## Permissions

The workflow needs:

```yaml
permissions:
  contents: write        # create tags/releases and push the release PR branch
  pull-requests: write   # open/update the release PR
```

If your org enforces "require approval for first-time contributors" on Actions,
approve the bot once. For a personal repo the default `GITHUB_TOKEN` is enough;
no PAT required.
