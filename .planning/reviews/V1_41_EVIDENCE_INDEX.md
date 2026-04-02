# v1.41 Evidence Index

**Purpose:** 为 `v1.41 Terminal Residual Audit, Remediation Charter & Maintainability Hardening` 提供 machine-readable archived evidence chain 入口，集中索引 `Phase 136` 的 promoted closeout bundle、milestone audit verdict 与 archived snapshots。
**Status:** Archived milestone evidence index (`archived / evidence-ready (2026-04-02)`)
**Updated:** 2026-04-02

## Pull Contract

- 本文件只索引正式真源、promoted closeout bundle、milestone audit 与 archive snapshots；它不是新的 authority source。
- `v1.41` 已完成 milestone closeout，并正式提升为 latest archived baseline；`v1.40` 退回 previous archived baseline 的 pull-only 身份。
- `.planning/v1.41-MILESTONE-AUDIT.md` 是 `v1.41` verdict home；`.planning/reviews/PROMOTED_PHASE_ASSETS.md` 是 promoted phase bundle allowlist 真源。
- 后续 `$gsd-new-milestone` 应以本文件登记的 archived evidence chain 作为 latest baseline 起点，不得重新扫描仓库拼装第二套 closeout 叙事。

## Previous Archived Baseline

- Previous archived baseline evidence: `.planning/reviews/V1_40_EVIDENCE_INDEX.md`
- Previous archived baseline audit: `.planning/v1.40-MILESTONE-AUDIT.md`
- Previous archived snapshots: `.planning/milestones/v1.40-ROADMAP.md`, `.planning/milestones/v1.40-REQUIREMENTS.md`

## Promoted Closeout Bundle

- `Phase 136` bundle: `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-01-SUMMARY.md`, `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-02-SUMMARY.md`, `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-03-SUMMARY.md`, `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-SUMMARY.md`, `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-VERIFICATION.md`, `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-VALIDATION.md`

## Milestone Closeout Bundle

- Milestone audit: `.planning/v1.41-MILESTONE-AUDIT.md`
- Evidence index: `.planning/reviews/V1_41_EVIDENCE_INDEX.md`
- Archived snapshots: `.planning/milestones/v1.41-ROADMAP.md`, `.planning/milestones/v1.41-REQUIREMENTS.md`
- Promoted allowlist home: `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- Current route truth: `no active milestone route / latest archived baseline = v1.41`
- Default next command: `$gsd-new-milestone`

## Validation Evidence

- Targeted production / seam lane: `83 passed`
- Governance / release / route lane: `146 passed`
- Targeted `ruff` slices: passed

## Non-Blocking Continuity Notes

- `v1.41` 的 repo-wide terminal 审阅、remediation charter、focused hygiene fixes 与 governance closeout 审阅已完成；当前具备完整 archived evidence coverage。
- future work 已被诚实压缩为 next milestone 候选：mega-facade slimming、auth hotspot decomposition、device facade rationalization、typed command grammar、governance derivation cost reduction、observability/log-safety follow-up。
- closeout 完成后，本文件应提升为 latest archived evidence pointer，`v1.40` 退为 previous archived baseline。
