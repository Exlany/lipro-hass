# v1.35 Evidence Index

**Purpose:** 为 `v1.35 Master Audit Closure, Public Surface Finalization & Release Traceability` 提供 machine-readable archived evidence chain 入口，集中索引 `Phase 122 -> 125` 的 promoted bundle、milestone audit verdict 与 archived snapshots。
**Status:** Archived milestone evidence index (`archived / evidence-ready (2026-04-01)`)
**Updated:** 2026-04-01

## Pull Contract

- 本文件只索引正式真源、promoted phase bundles、里程碑审计与 archived snapshots；它不是新的 authority source。
- `v1.35` 已固定为 latest archived baseline；`v1.34` 作为 previous archived baseline 保留 pull-only 身份。
- `.planning/v1.35-MILESTONE-AUDIT.md` 是 `v1.35` verdict home；`.planning/reviews/PROMOTED_PHASE_ASSETS.md` 是 phase closeout bundle allowlist 真源。
- 后续 closeout / archive promotion 必须 pull 本文件中登记的证据链，不得重扫仓库拼装第二套 closeout 叙事。

## Previous Archived Baseline

- Previous archived baseline evidence: `.planning/reviews/V1_34_EVIDENCE_INDEX.md`
- Previous archived baseline audit: `.planning/v1.34-MILESTONE-AUDIT.md`
- Previous archived snapshots: `.planning/milestones/{v1.34-ROADMAP.md,v1.34-REQUIREMENTS.md}`

## Promoted Closeout Bundles

- `Phase 122` bundle: `.planning/phases/122-master-audit-ledger-public-first-hop-boundary-finalization-metadata-traceability-and-focused-guard-sealing/{122-01-SUMMARY.md,122-02-SUMMARY.md,122-03-SUMMARY.md,122-VERIFICATION.md}`
- `Phase 123` bundle: `.planning/phases/123-service-router-family-reconvergence-control-plane-locality-tightening-and-public-architecture-hygiene/{123-01-SUMMARY.md,123-02-SUMMARY.md,123-03-SUMMARY.md,123-VERIFICATION.md}`
- `Phase 124` bundle: `.planning/phases/124-config-entry-auth-seed-normalization-config-flow-adapter-thinning-and-schedule-contract-closure/{124-01-SUMMARY.md,124-02-SUMMARY.md,124-03-SUMMARY.md,124-04-SUMMARY.md,124-05-SUMMARY.md,124-SUMMARY.md,124-VERIFICATION.md}`
- `Phase 125` bundle: `.planning/phases/125-terminal-residual-eradication-runtime-types-decomposition-adapter-final-thinning-and-machine-readable-governance-extraction/{125-01-SUMMARY.md,125-02-SUMMARY.md,125-03-SUMMARY.md,125-04-SUMMARY.md,125-05-SUMMARY.md,125-SUMMARY.md,125-VERIFICATION.md}`

## Milestone Closeout Bundle

- Milestone audit: `.planning/v1.35-MILESTONE-AUDIT.md`
- Evidence index: `.planning/reviews/V1_35_EVIDENCE_INDEX.md`
- Archived snapshots: `.planning/milestones/{v1.35-ROADMAP.md,v1.35-REQUIREMENTS.md}`
- Promoted allowlist home: `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- Current route truth: `no active milestone route / latest archived baseline = v1.35`
- Default next command: `$gsd-new-milestone`

## Non-Blocking Continuity Notes

- `Phase 122 -> 125` 未生成额外 `*-VALIDATION.md` Nyquist 资产；当前 archived verdict 继续依赖 `122-VERIFICATION.md`、`123-VERIFICATION.md`、`124-VERIFICATION.md`、`125-VERIFICATION.md`、focused regressions、`uv run ruff check .`、`uv run python scripts/check_file_matrix.py --check` 与 `uv run pytest -q` 的绿色证据链。
- repo-external continuity debt（private disclosure fallback / public mirror-HACS / delegate maintainer）仍保持 honest blocker posture；它们不是本轮 repo-internal delivery blocker。
