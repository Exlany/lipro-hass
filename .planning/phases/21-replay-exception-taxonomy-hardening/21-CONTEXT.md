# Phase 21 Context

**Phase:** `21 Replay Coverage & Exception Taxonomy Hardening`
**Milestone:** `v1.2 Host-Neutral Core & Replay Completion`
**Date:** `2026-03-16`
**Status:** `Ready for planning`
**Source:** `Phase 20` closeout truth + current roadmap/requirements/state + v1.2 endgame decomposition

## Why Phase 21 Exists

Phase 20 已完成 remaining boundary family formalization，但 replay/evidence 与异常分类仍未完全覆盖这些新 family；同时 protocol/runtime/control 关键链路里仍存在 broad-catch 与 failure-language 漂移。

## Goal

1. 把 Phase 20 新增 families 纳入 replay / evidence 正式链路。
2. 继续收窄 broad-catch，并形成可复用的 failure taxonomy contract。
3. 为 Phase 22 的 observability consumer convergence 提供稳定上游 truth。

## Decisions (Locked)

- 本 phase 不直接改 contributor docs / release closeout。
- failure taxonomy 必须先在 protocol/runtime/control 内部稳定，再向外暴露。
- replay/evidence 只能复用正式 public path，不重开 helper-local assertion story。

## Non-Negotiable Constraints

- 不得重开第二条正式主链、第二套 replay/evidence story 或第二套 governance authority。
- 不得把未在本 phase 范围内的问题偷跑进来，破坏 `21 -> 24` 的严格依赖链。
- 所有 phase 产出都必须可验证、可回写、可仲裁，并能被后续 phase 消费。
