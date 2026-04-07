# v1.34 Evidence Index

**Purpose:** 为 `v1.34 Terminal Audit Closure, Contract Hardening & Governance Truth Slimming` 提供 machine-readable closeout evidence chain 入口，集中索引 `Phase 120` 与 `Phase 121` 的 promoted bundle、milestone audit verdict 与 archived snapshots。
**Status:** Archived milestone evidence index (`archived / evidence-ready (2026-04-01)`)
**Updated:** 2026-04-01

## Pull Contract

- 本文件只索引正式真源、promoted phase bundles、里程碑审计与 archived snapshots；它不是新的 authority source。
- `v1.34` 已固定为 latest archived baseline；`v1.33` 作为 previous archived baseline 保留 pull-only 身份。
- `.planning/v1.34-MILESTONE-AUDIT.md` 是 `v1.34` verdict home；`.planning/reviews/PROMOTED_PHASE_ASSETS.md` 是 phase closeout bundle allowlist 真源。
- 后续 closeout / archive promotion 必须 pull 本文件中登记的证据链，不得重扫仓库拼装第二套 closeout 叙事。

## Previous Archived Baseline

- Previous archived baseline evidence: `.planning/reviews/V1_33_EVIDENCE_INDEX.md`
- Previous archived baseline audit: `.planning/v1.33-MILESTONE-AUDIT.md`
- Previous archived snapshots: `.planning/milestones/{v1.33-ROADMAP.md,v1.33-REQUIREMENTS.md}`

## Promoted Closeout Bundles

- `Phase 120` bundle: `.planning/phases/120-terminal-audit-contract-hardening-and-governance-truth-slimming/{120-01-SUMMARY.md,120-02-SUMMARY.md,120-03-SUMMARY.md,120-VERIFICATION.md}`
- `Phase 121` bundle: `.planning/phases/121-residual-contract-closure-flow-invariant-tightening-surface-hygiene-cleanup/{121-01-SUMMARY.md,121-02-SUMMARY.md,121-03-SUMMARY.md,121-VERIFICATION.md}`

## Milestone Closeout Bundle

- Milestone audit: `.planning/v1.34-MILESTONE-AUDIT.md`
- Evidence index: `.planning/reviews/V1_34_EVIDENCE_INDEX.md`
- Archived snapshots: `.planning/milestones/{v1.34-ROADMAP.md,v1.34-REQUIREMENTS.md}`
- Promoted allowlist home: `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- Current route truth: `no active milestone route / latest archived baseline = v1.34`
- Default next command: `$gsd-new-milestone`

## Non-Blocking Continuity Notes

- `Phase 120 -> 121` 未生成 `*-VALIDATION.md` Nyquist 资产；当前 archived verdict 继续依赖 `120-VERIFICATION.md`、`121-VERIFICATION.md`、focused regressions、`uv run ruff check .`、`uv run python scripts/check_file_matrix.py --check` 与 `uv run pytest -q` 的绿色证据链。
- repo-external continuity debt（private disclosure fallback / public mirror-HACS / delegate maintainer）仍保持 honest blocker posture；它们不是本轮 repo-internal delivery blocker。
