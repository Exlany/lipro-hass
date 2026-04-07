# Phase 22 Context

**Phase:** `22 Observability Surface Convergence & Signal Exposure`
**Milestone:** `v1.2 Host-Neutral Core & Replay Completion`
**Date:** `2026-03-16`
**Status:** `Ready for planning`
**Source:** `Phase 21` failure-taxonomy contract freeze + current roadmap/requirements/state + observability consumer reality audit

## Why Phase 22 Exists

`Phase 21` 若只把 failure taxonomy 冻结在 replay / telemetry formal truth 层，而 diagnostics / system health / developer / support / evidence consumers 仍各说各话，则 `OBS-03` 仍不成立。`Phase 22` 的职责不是再定义 taxonomy，而是让所有 consumer pull 同一 structured signals。

## Goal

1. 把 `Phase 21` 产出的 failure taxonomy 显式暴露给 diagnostics / system health。
2. 让 developer / support / report-building surfaces 复用同一 structured signals，而不是各自重算失败摘要。
3. 用 integration / meta / governance guards 阻断 observability consumer 再长出第二套 failure vocabulary。

## Decisions (Locked)

- 本 phase 只消费 `Phase 21` contract，不重新定义第二套 taxonomy。
- raw exception type 只能作为 debug detail；consumer-facing normalized fields 必须来自同一 formal truth。
- diagnostics / system health / developer / support / evidence consumers 只能 pull，不得各自局部仲裁失败语言。
- 本 phase 不改 contributor docs / release workflow / archive closeout；这些留给 `Phase 23-24`。

## Non-Negotiable Constraints

- 不得重开第二条正式主链、第二套 replay/evidence story 或第二套 governance authority。
- 不得偷跑 `Phase 23` 的 docs/templates/release gate 工作，或 `Phase 24` 的 archive/handoff 工作。
- 所有 phase 产出都必须可验证、可回写、可仲裁，并能被后续 phase 消费。
