# v1.43 Evidence Index

**Purpose:** 为 `v1.43 Hotspot Second-Pass Slimming & Governance Load Shedding` 提供 machine-readable archived evidence chain 入口，集中索引 `Phase 139`、`Phase 140` 与 `Phase 141` 的 promoted closeout bundle、milestone audit verdict 与 archived snapshots。
**Status:** Archived milestone evidence index (`archived / evidence-ready (2026-04-04)`)
**Updated:** 2026-04-04

## Pull Contract

- 本文件只索引正式真源、promoted closeout bundle、milestone audit 与 archive snapshots；它不是新的 authority source。
- `v1.43` 已完成 milestone closeout，并正式提升为 latest archived baseline；`v1.42` 退回 previous archived baseline 的 pull-only 身份。
- `.planning/v1.43-MILESTONE-AUDIT.md` 是 `v1.43` verdict home；`.planning/reviews/PROMOTED_PHASE_ASSETS.md` 是 promoted phase bundle allowlist 真源。
- 后续 `$gsd-new-milestone` 应以本文件登记的 archived evidence chain 作为 latest baseline 起点，不得重新扫描仓库拼装第二套 closeout 叙事。

## Previous Archived Baseline

- Previous archived baseline evidence: `.planning/reviews/V1_42_EVIDENCE_INDEX.md`
- Previous archived baseline audit: `.planning/v1.42-MILESTONE-AUDIT.md`
- Previous archived snapshots: `.planning/milestones/v1.42-ROADMAP.md`, `.planning/milestones/v1.42-REQUIREMENTS.md`

## Promoted Closeout Bundle

- `Phase 139` bundle: `.planning/phases/139-rest-protocol-surface-second-pass-slimming-and-boundary-hardening/139-01-SUMMARY.md`, `.planning/phases/139-rest-protocol-surface-second-pass-slimming-and-boundary-hardening/139-02-SUMMARY.md`, `.planning/phases/139-rest-protocol-surface-second-pass-slimming-and-boundary-hardening/139-03-SUMMARY.md`, `.planning/phases/139-rest-protocol-surface-second-pass-slimming-and-boundary-hardening/139-SUMMARY.md`, `.planning/phases/139-rest-protocol-surface-second-pass-slimming-and-boundary-hardening/139-VERIFICATION.md`, `.planning/phases/139-rest-protocol-surface-second-pass-slimming-and-boundary-hardening/139-VALIDATION.md`
- `Phase 140` bundle: `.planning/phases/140-release-governance-source-compression-and-codebase-freshness/140-01-SUMMARY.md`, `.planning/phases/140-release-governance-source-compression-and-codebase-freshness/140-02-SUMMARY.md`, `.planning/phases/140-release-governance-source-compression-and-codebase-freshness/140-03-SUMMARY.md`, `.planning/phases/140-release-governance-source-compression-and-codebase-freshness/140-SUMMARY.md`, `.planning/phases/140-release-governance-source-compression-and-codebase-freshness/140-VERIFICATION.md`, `.planning/phases/140-release-governance-source-compression-and-codebase-freshness/140-VALIDATION.md`
- `Phase 141` bundle: `.planning/phases/141-control-runtime-hotspot-narrowing-and-device-aggregate-hardening/141-01-SUMMARY.md`, `.planning/phases/141-control-runtime-hotspot-narrowing-and-device-aggregate-hardening/141-02-SUMMARY.md`, `.planning/phases/141-control-runtime-hotspot-narrowing-and-device-aggregate-hardening/141-03-SUMMARY.md`, `.planning/phases/141-control-runtime-hotspot-narrowing-and-device-aggregate-hardening/141-04-SUMMARY.md`, `.planning/phases/141-control-runtime-hotspot-narrowing-and-device-aggregate-hardening/141-05-SUMMARY.md`, `.planning/phases/141-control-runtime-hotspot-narrowing-and-device-aggregate-hardening/141-SUMMARY.md`, `.planning/phases/141-control-runtime-hotspot-narrowing-and-device-aggregate-hardening/141-VERIFICATION.md`, `.planning/phases/141-control-runtime-hotspot-narrowing-and-device-aggregate-hardening/141-VALIDATION.md`

## Milestone Closeout Bundle

- Milestone audit: `.planning/v1.43-MILESTONE-AUDIT.md`
- Evidence index: `.planning/reviews/V1_43_EVIDENCE_INDEX.md`
- Archived snapshots: `.planning/milestones/v1.43-ROADMAP.md`, `.planning/milestones/v1.43-REQUIREMENTS.md`
- Promoted allowlist home: `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- Current route truth: `no active milestone route / latest archived baseline = v1.43`
- Default next command: `$gsd-new-milestone`

## Validation Evidence

- Protocol / API second-pass lane: passed
- Release / governance freshness lane: `150 passed`
- Control / runtime / device / governance lane: `177 passed`
- Repository-wide regression lane: `2772 passed`
- `uv run ruff check .`: passed
- `scripts/check_file_matrix.py --check`: passed
- `scripts/check_architecture_policy.py --check`: passed

## Non-Blocking Continuity Notes

- `v1.43` 的 REST/protocol second-pass slimming、release/governance freshness formalization、control/runtime hotspot narrowing、device aggregate/runtime side-car hardening 与 closeout 审计已共同形成完整 archived evidence coverage。
- future work 必须从 `v1.43` archived evidence 与 next milestone selector 显式衔接，不得回写成仍在执行中的 active route。
- closeout 完成后，本文件已提升为 latest archived evidence pointer，`v1.42` 退为 previous archived baseline。
