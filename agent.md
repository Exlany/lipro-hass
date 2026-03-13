# agent.md

> Pointer only — this file does **not** define a second rule set.

## Purpose

- 只作为恢复上下文与导航索引。
- 不新增规则、不改写 `AGENTS.md`、不覆盖 north-star / `.planning/*` 真源。

## Read Order

1. `AGENTS.md`
2. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/phases/07.3-runtime-telemetry-exporter/07.3-CONTEXT.md`
7. `.planning/phases/07.4-protocol-replay-simulator-harness/07.4-CONTEXT.md`
8. `.planning/phases/08-ai-debug-evidence-pack/08-CONTEXT.md`
9. `.planning/phases/07.2-architecture-enforcement/07.2-CONTEXT.md`
10. `.planning/phases/07.2-architecture-enforcement/07.2-RESEARCH.md`
11. `.planning/phases/07.2-architecture-enforcement/07.2-ARCHITECTURE.md`
12. `.planning/phases/07.2-architecture-enforcement/07.2-VALIDATION.md`
13. `.planning/phases/07.2-architecture-enforcement/07.2-01-PLAN.md`
14. `.planning/phases/07.2-architecture-enforcement/07.2-02-PLAN.md`
15. `.planning/baseline/*.md`
16. `.planning/reviews/*.md`
17. `docs/developer_architecture.md`

## Current Focus

- Active milestone: `v1.1 Protocol Fidelity & Operability`
- Active phase: `Phase 7.3 Runtime Telemetry Exporter 正式化`
- Current state: `v1.1 planning`
- Recommended next command: `$gsd-plan-phase 7.3`

## Rules

- 若 `agent.md` 与 `AGENTS.md` 冲突，以 `AGENTS.md` 为准。
- 若执行入口与架构文档冲突，以 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` + `.planning/*` + `.planning/reviews/*` 为准。
- `agent.md` 只负责指路，不负责定义新 truth source。
- 历史执行/审计/归档文档只作参考，不参与当前仲裁。

## North Star 2.0 Pointer

- 北极星 2.0（AI Debug Ready, HA-only）已写入：`docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 与 `.planning/*`。
- 关键产物路线：`07.3 telemetry exporter` → `07.4 replay harness` → `07.5 closeout` → `08 AI debug evidence pack`。
