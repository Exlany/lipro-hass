---
phase: 131-repo-wide-terminal-audit-closeout-and-governance-continuity-decisions
plan: "02"
summary: true
---

# Plan 131-02 Summary

## Completed

- 修正文档首跳与 follow-up routing：`docs/README.md`、`CONTRIBUTING.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 现在共同承认 docs-first / private-access / maintainer-only appendix 的真实边界。
- 修正 Python/toolchain truth：`pyproject.toml` 与 `.planning/baseline/GOVERNANCE_REGISTRY.json` 恢复 patch-accurate floor `>=3.14.2`，同时保留 CI/devcontainer/pre-commit/mypy 的 `3.14` minor-family 目标叙事。
- 修正 install-surface honesty：registry 继续把 `verified_release_assets` 作为 stable path，仅把 `HACS` 保留为 conditional path。

## Outcome

- docs / registry / toolchain 现在讲同一条 current story，不再出现 public first hop、自身 follow-up 路由、Python floor 与 install semantics 互相打架的情况。
- private-access clone、conditional GitHub surfaces 与 single-maintainer continuity 都被前推为显式 contract，而不是口头默认值。
