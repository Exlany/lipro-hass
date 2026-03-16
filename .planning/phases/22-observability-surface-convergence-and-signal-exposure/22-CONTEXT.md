# Phase 22 Context

**Phase:** `22 Observability Surface Convergence & Signal Exposure`
**Milestone:** `v1.2 Host-Neutral Core & Replay Completion`
**Date:** `2026-03-16`
**Status:** `Ready for planning`
**Source:** `Phase 20` closeout truth + current roadmap/requirements/state + v1.2 endgame decomposition

## Why Phase 22 Exists

Phase 21 若只完成内部 taxonomy，而 diagnostics/system health/support/developer surfaces 仍各说各话，则 observability 仍会漂移。

## Goal

1. 把 classified failure signals 暴露到 diagnostics / system health。
2. 让 support / developer / report consumers 复用同一 structured signals。
3. 用 integration/meta guards 阻断第二套 failure vocabulary。

## Decisions (Locked)

- 本 phase 不重开 replay family formalization。
- consumer convergence 优先于 UI/wording 美化。
- 对外 surfaces 只能 pull 同一 structured signals，不得局部重算。

## Non-Negotiable Constraints

- 不得重开第二条正式主链、第二套 replay/evidence story 或第二套 governance authority。
- 不得把未在本 phase 范围内的问题偷跑进来，破坏 `21 -> 24` 的严格依赖链。
- 所有 phase 产出都必须可验证、可回写、可仲裁，并能被后续 phase 消费。
