# v1.42 Evidence Index

**Purpose:** 为 `v1.42 Hotspot Burn-Down, Observability Truth & Governance Cost Compression` 提供 machine-readable archived evidence chain 入口，集中索引 `Phase 137` 与 `Phase 138` 的 promoted closeout bundle、milestone audit verdict 与 archived snapshots。
**Status:** Archived milestone evidence index (`archived / evidence-ready (2026-04-02)`)
**Updated:** 2026-04-02

## Pull Contract

- 本文件只索引正式真源、promoted closeout bundle、milestone audit 与 archive snapshots；它不是新的 authority source。
- `v1.42` 已完成 milestone closeout，并正式提升为 latest archived baseline；`v1.41` 退回 previous archived baseline 的 pull-only 身份。
- `.planning/v1.42-MILESTONE-AUDIT.md` 是 `v1.42` verdict home；`.planning/reviews/PROMOTED_PHASE_ASSETS.md` 是 promoted phase bundle allowlist 真源。
- 后续 `$gsd-new-milestone` 应以本文件登记的 archived evidence chain 作为 latest baseline 起点，不得重新扫描仓库拼装第二套 closeout 叙事。

## Previous Archived Baseline

- Previous archived baseline evidence: `.planning/reviews/V1_41_EVIDENCE_INDEX.md`
- Previous archived baseline audit: `.planning/v1.41-MILESTONE-AUDIT.md`
- Previous archived snapshots: `.planning/milestones/v1.41-ROADMAP.md, .planning/milestones/v1.41-REQUIREMENTS.md`

## Promoted Closeout Bundle

- `Phase 137` bundle: `.planning/phases/137-hotspot-burn-down-command-observability-and-governance-compression/137-01-SUMMARY.md`, `.planning/phases/137-hotspot-burn-down-command-observability-and-governance-compression/137-02-SUMMARY.md`, `.planning/phases/137-hotspot-burn-down-command-observability-and-governance-compression/137-03-SUMMARY.md`, `.planning/phases/137-hotspot-burn-down-command-observability-and-governance-compression/137-SUMMARY.md`, `.planning/phases/137-hotspot-burn-down-command-observability-and-governance-compression/137-VERIFICATION.md`, `.planning/phases/137-hotspot-burn-down-command-observability-and-governance-compression/137-VALIDATION.md`
- `Phase 138` bundle: `.planning/phases/138-runtime-contract-decoupling-support-guard-and-docs-alignment/138-01-SUMMARY.md`, `.planning/phases/138-runtime-contract-decoupling-support-guard-and-docs-alignment/138-02-SUMMARY.md`, `.planning/phases/138-runtime-contract-decoupling-support-guard-and-docs-alignment/138-03-SUMMARY.md`, `.planning/phases/138-runtime-contract-decoupling-support-guard-and-docs-alignment/138-04-SUMMARY.md`, `.planning/phases/138-runtime-contract-decoupling-support-guard-and-docs-alignment/138-SUMMARY.md`, `.planning/phases/138-runtime-contract-decoupling-support-guard-and-docs-alignment/138-VERIFICATION.md`, `.planning/phases/138-runtime-contract-decoupling-support-guard-and-docs-alignment/138-VALIDATION.md`

## Milestone Closeout Bundle

- Milestone audit: `.planning/v1.42-MILESTONE-AUDIT.md`
- Evidence index: `.planning/reviews/V1_42_EVIDENCE_INDEX.md`
- Archived snapshots: `.planning/milestones/v1.42-ROADMAP.md, .planning/milestones/v1.42-REQUIREMENTS.md`
- Promoted allowlist home: `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- Current route truth: `no active milestone route / latest archived baseline = v1.42`
- Default next command: `$gsd-new-milestone`

## Validation Evidence

- Targeted API / protocol lane: `33 passed`
- Governance / release / route lane: `22 passed`
- Combined focused regression lane: `119 passed`
- Targeted `ruff` slices: passed
- `scripts/check_file_matrix.py --check`: passed
- `scripts/check_architecture_policy.py --check`: passed

## Non-Blocking Continuity Notes

- `v1.42` 的 hotspot burn-down、runtime/service contract decoupling、connect-status outward outcome formalization、support bridge guard hardening 与 docs/archive alignment 已共同形成完整 archived evidence coverage。
- future work 必须从 `v1.42` archived evidence 与 next milestone selector 显式衔接，不得回写成仍在执行中的 active route。
- closeout 完成后，本文件已提升为 latest archived evidence pointer，`v1.41` 退为 previous archived baseline。
