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
6. `.planning/phases/07.5-integration-governance-verification-closeout/07.5-SUMMARY.md`
7. `.planning/phases/07.5-integration-governance-verification-closeout/07.5-VERIFICATION.md`
8. `.planning/phases/08-ai-debug-evidence-pack/08-ARCHITECTURE.md`
9. `.planning/phases/08-ai-debug-evidence-pack/08-VALIDATION.md`
10. `.planning/phases/08-ai-debug-evidence-pack/08-01-SUMMARY.md`
11. `.planning/phases/08-ai-debug-evidence-pack/08-02-SUMMARY.md`
12. `.planning/phases/08-ai-debug-evidence-pack/08-VERIFICATION.md`
13. `.planning/baseline/*.md`
14. `.planning/reviews/*.md`
15. `docs/developer_architecture.md`

## Current Focus

- Active milestone: `v1.1 Protocol Fidelity & Operability`
- Active phase: `Phase 8 AI Debug Evidence Pack 已完成`
- Current state: `verification pending`
- Recommended next command: `$gsd-verify-work 7.5`

## Rules

- 若 `agent.md` 与 `AGENTS.md` 冲突，以 `AGENTS.md` 为准。
- 若执行入口与架构文档冲突，以 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` + `.planning/*` + `.planning/reviews/*` 为准。
- `agent.md` 只负责指路，不负责定义新 truth source。
- 历史执行/审计/归档文档只作参考，不参与当前仲裁。

## North Star 2.0 Pointer

- 北极星 2.0（AI Debug Ready, HA-only）已写入：`docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 与 `.planning/*`。
- 当前主链已收束为：`07.3 telemetry exporter` → `07.4 replay harness` → `07.5 closeout` → `08 AI debug evidence pack`。
- 接下来只做 `verify-work 7.5 / 8` 的对话式验收，不再新增第二条事实链。
