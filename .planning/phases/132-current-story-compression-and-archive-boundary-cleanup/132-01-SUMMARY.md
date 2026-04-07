---
phase: 132-current-story-compression-and-archive-boundary-cleanup
plan: "01"
summary: true
---

# Plan 132-01 Summary

## Completed

- 将 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` 与 `.planning/baseline/GOVERNANCE_REGISTRY.json` 首屏统一到 `v1.38 active milestone route / starting from latest archived baseline = v1.37`。
- 将 `docs/developer_architecture.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 的 first hop 改回 current-entry 叙事，保留 `v1.37` 作为 pull-only latest archived pointer。
- 保持 archived milestone blocks 为历史回溯用途，不再把 archived-only closeout 语气混回 live selector 入口。

## Outcome

- planning docs、developer docs 与 maintainer runbook 现在共同承认同一条 current route，不再出现 archived baseline frozen 口径占据 live entry 的漂移。
- `v1.37` 继续只作为 latest archived evidence family 暴露，而不是被误写成当前默认路线。
