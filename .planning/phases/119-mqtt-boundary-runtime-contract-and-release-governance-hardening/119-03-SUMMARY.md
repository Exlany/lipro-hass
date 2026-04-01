# Plan 119-03 Summary

## What changed
- `.github/workflows/{release,codeql}.yml` 已收窄到 semver-only tag namespace。
- `tests/meta/governance_current_truth.py` 现直接读取 `.planning/PROJECT.md` route contract，成为 route handoff / follow-up / release docs 的 shared canonical helper。
- `.planning` live docs、`docs/developer_architecture.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md` 与 `CHANGELOG.md` 已统一到 `v1.33 active route / Phase 119 complete; closeout-ready` 的单一故事。

## Outcome
- public release / governance story 不再并存旧 archived-route hardcode、内部 tag namespace 与 stale changelog pointer。
- `v1.33` 当前已进入 milestone closeout-ready。
