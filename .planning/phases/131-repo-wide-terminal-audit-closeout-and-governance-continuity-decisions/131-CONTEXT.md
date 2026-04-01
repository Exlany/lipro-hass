# Phase 131: repo-wide terminal audit closeout and governance continuity decisions - 背景

**Gathered:** 2026-04-01
**Status:** 规划就绪
**Source:** Phase 130 closeout + 契约者终极审阅指令

<domain>
## 阶段边界

本阶段承接 `AUD-06, GOV-87, DOC-16, OSS-18, QLT-53`，目标不是再开新一轮热点拆分，而是把已经完成的 repo-wide 代码/文档/配置/governance 审阅结果收敛成单一 current truth：统一终审报告、热点排序、remaining boundary、开源不足与最终 validation evidence，并把无法在仓内凭空创造的 continuity / private-fallback 现实明确 codify 为 decision boundary。

</domain>

<decisions>
## 实施决策

### Locked Decisions
- `Phase 131` 必须覆盖全部 Python / docs / config / governance 切面，输出单一终审结论，而不是散落在聊天、零散 summary 或私有上下文里。
- 允许继续刷新 docs / ledgers / governance truth / validation proof；除非审阅发现新的 blocker，否则不再发起大范围生产代码拆分。
- 对 repo-external continuity、delegate stewardship 与 private fallback 只能陈述仓内真实状态；允许仓内补充 compensating controls，但不得伪造不存在的能力。
- 最终报告必须把“已修复 / 已冻结 / 诚实保留为边界”的三类结论分开写清楚。

### the agent's Discretion
- 审阅报告的章节结构、风险分级与 phase mapping 呈现方式。
- 是否需要新增轻量 governance smoke / docs guard，只要仍遵守 minimal change 与 evidence-first 原则。

</decisions>

<canonical_refs>
## 权威参考

### Route / Governance Truth
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`
- `.planning/baseline/VERIFICATION_MATRIX.md`

### Audit / Review Ledgers
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/V1_36_EVIDENCE_INDEX.md`
- `.planning/v1.36-MILESTONE-AUDIT.md`

### Codebase / Public Docs
- `.planning/codebase/{ARCHITECTURE.md,STRUCTURE.md,CONCERNS.md,CONVENTIONS.md,TESTING.md}`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `README.md`
- `README_zh.md`
- `CONTRIBUTING.md`
- `SECURITY.md`

### Recent Phase Evidence
- `.planning/phases/129-rest-fallback-explicit-surface-convergence-and-api-hotspot-slimming/{129-SUMMARY.md,129-VERIFICATION.md,129-VALIDATION.md}`
- `.planning/phases/130-runtime-command-and-firmware-update-hotspot-decomposition/{130-SUMMARY.md,130-VERIFICATION.md,130-VALIDATION.md}`

</canonical_refs>

<specifics>
## 具体关注点

- 统一 repo-wide terminal audit 报告：架构先进性、目录可维护性、命名规范、重构残留、文档/治理诚实度、开源 readiness。
- 明确 remaining decision boundary：哪些是仓内已解决，哪些是仓内可进一步治理，哪些只能保留为 repo-external honesty。
- 形成最终 validation proof，并让 `$gsd-next` / governance route / final report 不再互相打架。

</specifics>

<deferred>
## 延后事项

- 若 `Phase 131` 结束后仍出现需要新代码改造的 blocker，应通过新 milestone 或 decimal phase 显式开线，而不是偷偷继续扩写 v1.37。

</deferred>
