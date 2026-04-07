---
phase: 128-open-source-readiness-benchmark-coverage-gates-and-maintainer-continuity-hardening
plan: "01"
summary: true
---

# Plan 128-01 Summary

## Completed

- `SECURITY.md` 与 `.github/ISSUE_TEMPLATE/bug.yml` 已把最低支持 Home Assistant 版本的 canonical source 明确统一到 `hacs.json`，`pyproject.toml` 只保留 dev pin / sync-source 身份。
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 已回到 selector projection 身份：current route 以 `.planning/baseline/GOVERNANCE_REGISTRY.json::planning_route` 为单一 machine-readable truth，不再手写第二条 archived-only current story。
- `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` 与 registry 已同步前推到 `active / phase 128 complete; closeout-ready (2026-04-01)`，默认下一步统一为 `$gsd-complete-milestone v1.36`。
- `CONTRIBUTING.md` 与 `.github/pull_request_template.md` 已把 readiness honesty、single-maintainer continuity、baseline-aware coverage compare 与 benchmark smoke 的 contributor contract 写成一致入口。

## Outcome

- `OSS-17` 与 `GOV-86` 已在 docs / templates / registry / selector family 内完成 codify。
- repo-external operational limits 仍保持诚实显式：没有 documented delegate、没有 guaranteed non-GitHub private fallback；这些限制被记录，而不是被伪装成已解决能力。
