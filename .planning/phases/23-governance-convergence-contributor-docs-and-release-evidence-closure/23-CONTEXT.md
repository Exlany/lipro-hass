# Phase 23 Context

**Phase:** `23 Governance convergence, contributor docs and release evidence closure`
**Milestone:** `v1.2 Host-Neutral Core & Replay Completion`
**Date:** `2026-03-16`
**Status:** `Ready for planning`
**Source:** `Phase 22` observability-contract closeout truth + current roadmap/requirements/state + v1.2 final-governance chain

## Why Phase 23 Exists

即使 `Phase 21-22` 已把 replay / taxonomy / consumer convergence 做对，如果 baseline/reviews、README/support/security、issue/PR 模板、maintainer runbook 与 release evidence 仍没有讲同一条故事，`GOV-16/GOV-17` 依然未达成。

## Goal

1. 把 `Phase 21-22` 真相同步到长期治理真源与 phase lifecycle truth。
2. 把 contributor-facing docs / templates / troubleshooting / support / security / version entry points 对齐到最终 v1.2 故事线。
3. 让 release evidence 与 CI/release gate 共享同一 authority / verification chain，而不是形成旁路发版故事。

## Decisions (Locked)

- baseline / reviews / roadmap-state truth 先于 README / SUPPORT / SECURITY / templates。
- release evidence 必须复用既有 CI + governance chain；不得自己发明 release-only 审核体系。
- `v1.2` 最终 milestone audit / archive-ready bundle / v1.3 handoff 留给 `Phase 24`。

## Non-Negotiable Constraints

- 不得在本 phase 里继续修改 production implementation semantics；这里只收 governance / docs / release evidence truth。
- 不得把 `Phase 24` 的 final repo audit / milestone archival / handoff decision 偷跑进来。
- 任何 contributor-facing 入口变更都必须同步 `docs/TROUBLESHOOTING.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md`，禁止 silent drift。
