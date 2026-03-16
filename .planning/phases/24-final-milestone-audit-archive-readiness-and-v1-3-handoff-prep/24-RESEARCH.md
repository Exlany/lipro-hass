# Phase 24 Research

**Status:** `research complete`
**Date:** `2026-03-16`
**Mode:** `deep refinement after Phase 22-23 planning`
**Requirement:** `GOV-18`

## Executive Judgment

`Phase 24` 是 `v1.2` 的真正收官相：它不负责再“修东西”，而负责**把已经做完的东西审干净、归档好、交接清楚**。

最优拆分是 `3 plans / 3 waves`：

1. `24-01`：final repo audit + residual arbitration
2. `24-02`：milestone audit + archive-ready bundle assembly
3. `24-03`：v1.3 handoff + next-phase seed + lifecycle transition truth

## Closeout Reality Audit

### 1. v1.2 milestone audit 资产目前尚不存在

仓库已有：

- `.planning/v1.1-MILESTONE-AUDIT.md`
- `.planning/MILESTONES.md`
- `.planning/reviews/V1_1_EVIDENCE_INDEX.md`

当前缺失：

- `.planning/v1.2-MILESTONE-AUDIT.md`
- `v1.2` 对应的 closeout-ready evidence pointer（若 23 未创建，则 24 必须消费/完成）
- `v1.3` handoff 文档

**结论：** `24-02` 与 `24-03` 不能只是更新 `ROADMAP/STATE`，必须交付真正的 milestone closeout assets。

### 2. final repo audit 不能只靠一行“tests all green”结束

结合 `Phase 16/17` 审计样式，`Phase 24-01` 应至少明确：

- residual / kill list / file ownership 的最终 disposition
- repo-wide audit counts（例如 `Any` / `except Exception` / `type: ignore` / dead markers 等）
- 有没有新的无主高风险残留
- 哪些项被明确 defer 到 `v1.3`，以及为什么

**裁决：** final repo audit 必须落成可阅读的明确资产，而不是散落在 PR 描述或 phase summary 里。

### 3. archive-ready 不等于立即 archive，但必须形成可归档状态

`ROADMAP.md` 当前已把 `Phase 24` 描述为 archive readiness / handoff prep。这意味着：

- 可以先把 v1.2 milestone audit / evidence bundle / handoff 准备好
- 是否执行实际 milestone archival，可由后续 milestone-complete 类流程完成
- 但 `Phase 24` 自身必须保证：如果现在要 archive，不会因为缺失 closeout truth 而卡住

### 4. v1.3 handoff 需要显式文档，而不是仅在 STATE 里留一句 next command

若 `Phase 24-03` 只改 `PROJECT/ROADMAP/STATE/REQUIREMENTS` 而不留下 handoff doc，下一轮仍容易丢失：

- 哪些 debt 明确 defer
- 下一里程碑的北极星范围
- 不应再重开的旧争议
- 推荐的第一相位 seed

**结论：** `24-03` 最好创建 `v1.3-HANDOFF.md` 或等价显式 handoff asset，并同步 lifecycle docs。

## Recommended Plan Structure

### Plan 24-01 — final repo audit and residual arbitration

**建议文件域：**
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `tests/meta/test_governance_guards.py`

**必须达成：**
- 所有 remaining items 都有 close / retain / defer disposition。
- repo audit counts 与 high-risk residual ownership 形成显式记录。
- 无 silent defer。

### Plan 24-02 — assemble milestone audit and archive-ready bundle

**建议文件域：**
- `.planning/v1.2-MILESTONE-AUDIT.md`
- `.planning/MILESTONES.md`
- `.planning/reviews/V1_2_EVIDENCE_INDEX.md`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_version_sync.py`

**必须达成：**
- `v1.2` 有完整的 milestone scorecard / requirement coverage / phase coverage / audit verdict。
- archive-ready bundle 能单独说明“现在归档也不会丢真相”。
- 不提前写 `v1.3` active execution story。

### Plan 24-03 — write v1.3 handoff and transition lifecycle truth

**建议文件域：**
- `.planning/v1.3-HANDOFF.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`

**必须达成：**
- 下一里程碑 seed、deferred debt、禁止回流点与第一步建议都被显式写出。
- lifecycle docs 反映 `v1.2` closeout 完成、`v1.3` handoff ready。
- 不把未仲裁的 debt 带着进入下一轮。

## Risks And Boundaries

### Risk 1 — 把 final audit 当成“再做一轮零散修复”

**控制：** 24 只做审计/仲裁/归档/交接，不再扩实现范围。

### Risk 2 — milestone audit 与 evidence bundle 各写一套故事

**控制：** 24-02 必须让 milestone audit、evidence index、MILESTONES registry 相互引用。

### Risk 3 — 只更新 state，不写 handoff doc

**控制：** 24-03 必须交付显式 handoff asset，而不是把 handoff 压缩成一行 next command。

### Risk 4 — 把 archive-ready 与实际 archival 混淆

**控制：** 24 只保证 closeout assets ready；是否执行外层 archival，可在后续流程处理。
