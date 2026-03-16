# Phase 24 Research

**Status:** `draft research complete`
**Date:** `2026-03-16`

## Key Findings

- 当前 `v1.2` 已完成 `Phase 18-20`，因此 `Final milestone audit, archive readiness and v1.3 handoff prep` 不再需要为 remaining boundary family formalization 背锅，而应消费 `Phase 20` 结果继续前进。
- 本 phase 的 requirement set 为 `GOV-18`；执行时必须保持与 `.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md` 三处一致。
- 本 phase 应拆成 3 个 plans，按照 wave 顺序推进：先落核心 truth，再做 surface/gate/gov closeout。

## Recommended Breakdown

- **Plan 24-01**：run final repo audit and residual arbitration；主要文件域：.planning/reviews/RESIDUAL_LEDGER.md, .planning/reviews/KILL_LIST.md, .planning/reviews/FILE_MATRIX.md, tests/meta/test_governance_guards.py
- **Plan 24-02**：assemble milestone verification and archive bundle；主要文件域：.planning/phases/, .planning/MILESTONES.md, .planning/v1.2-MILESTONE-AUDIT.md
- **Plan 24-03**：write v1.3 handoff and next-phase seed；主要文件域：.planning/PROJECT.md, .planning/ROADMAP.md, .planning/STATE.md, .planning/REQUIREMENTS.md

## Risks To Watch

- 不要把跨 phase 工作揉成一个 megaphase；每一相只交付自身 must-have。
- 所有 docs/governance 变更都必须跟实现真相同轮更新，禁止“先写 README，后补实现/guard”。
- 若执行中发现新 requirement，必须先仲裁是否属于 `v1.2` 还是应 defer 到 `v1.3`。
