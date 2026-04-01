
# v1.36 Evidence Index

**Purpose:** 为 `v1.36 Terminal Residual Convergence, Runtime Access De-Reflection & Open-Source Readiness Hardening` 提供 machine-readable archived evidence chain 入口，集中索引 `Phase 126 -> 128` 的 promoted bundle、milestone audit verdict 与 archived snapshots。
**Status:** Archived milestone evidence index (`archived / evidence-ready (2026-04-01)`)
**Updated:** 2026-04-01

## Pull Contract

- 本文件只索引正式真源、promoted phase bundles、里程碑审计与 archived snapshots；它不是新的 authority source。
- `v1.36` 已固定为 latest archived baseline；`v1.35` 作为 previous archived baseline 保留 pull-only 身份。
- `.planning/v1.36-MILESTONE-AUDIT.md` 是 `v1.36` verdict home；`.planning/reviews/PROMOTED_PHASE_ASSETS.md` 是 phase closeout bundle allowlist 真源。
- 后续 closeout / archive promotion 必须 pull 本文件中登记的证据链，不得重扫仓库拼装第二套 closeout 叙事。

## Previous Archived Baseline

- Previous archived baseline evidence: `.planning/reviews/V1_35_EVIDENCE_INDEX.md`
- Previous archived baseline audit: `.planning/v1.35-MILESTONE-AUDIT.md`
- Previous archived snapshots: `.planning/milestones/v1.35-ROADMAP.md`, `.planning/milestones/v1.35-REQUIREMENTS.md`

## Promoted Closeout Bundles

- `Phase 126` bundle: `.planning/phases/126-service-router-developer-callback-home-convergence-and-diagnostics-helper-residual-slimming/126-01-SUMMARY.md`, `.planning/phases/126-service-router-developer-callback-home-convergence-and-diagnostics-helper-residual-slimming/126-SUMMARY.md`, `.planning/phases/126-service-router-developer-callback-home-convergence-and-diagnostics-helper-residual-slimming/126-VERIFICATION.md`
- `Phase 127` bundle: `.planning/phases/127-runtime-access-de-reflection-typed-runtime-entry-contracts-and-hotspot-continuation/127-01-SUMMARY.md`, `.planning/phases/127-runtime-access-de-reflection-typed-runtime-entry-contracts-and-hotspot-continuation/127-02-SUMMARY.md`, `.planning/phases/127-runtime-access-de-reflection-typed-runtime-entry-contracts-and-hotspot-continuation/127-03-SUMMARY.md`, `.planning/phases/127-runtime-access-de-reflection-typed-runtime-entry-contracts-and-hotspot-continuation/127-SUMMARY.md`, `.planning/phases/127-runtime-access-de-reflection-typed-runtime-entry-contracts-and-hotspot-continuation/127-VERIFICATION.md`, `.planning/phases/127-runtime-access-de-reflection-typed-runtime-entry-contracts-and-hotspot-continuation/127-VALIDATION.md`
- `Phase 128` bundle: `.planning/phases/128-open-source-readiness-benchmark-coverage-gates-and-maintainer-continuity-hardening/128-01-SUMMARY.md`, `.planning/phases/128-open-source-readiness-benchmark-coverage-gates-and-maintainer-continuity-hardening/128-02-SUMMARY.md`, `.planning/phases/128-open-source-readiness-benchmark-coverage-gates-and-maintainer-continuity-hardening/128-03-SUMMARY.md`, `.planning/phases/128-open-source-readiness-benchmark-coverage-gates-and-maintainer-continuity-hardening/128-SUMMARY.md`, `.planning/phases/128-open-source-readiness-benchmark-coverage-gates-and-maintainer-continuity-hardening/128-VERIFICATION.md`, `.planning/phases/128-open-source-readiness-benchmark-coverage-gates-and-maintainer-continuity-hardening/128-VALIDATION.md`

## Milestone Closeout Bundle

- Milestone audit: `.planning/v1.36-MILESTONE-AUDIT.md`
- Evidence index: `.planning/reviews/V1_36_EVIDENCE_INDEX.md`
- Archived snapshots: `.planning/milestones/v1.36-ROADMAP.md`, `.planning/milestones/v1.36-REQUIREMENTS.md`
- Promoted allowlist home: `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- Current route truth: `no active milestone route / latest archived baseline = v1.36`
- Default next command: `$gsd-new-milestone`

## Non-Blocking Continuity Notes

- `Phase 126` 未生成额外 `126-VALIDATION.md` Nyquist 资产；当前 archived verdict 继续依赖 `126-VERIFICATION.md`、`127-VERIFICATION.md`、`128-VERIFICATION.md`、focused regressions、`uv run ruff check .`、`uv run python scripts/check_file_matrix.py --check`、benchmark smoke 与 `uv run pytest -q` 的绿色证据链。
- repo-external continuity debt（documented delegate maintainer / guaranteed non-GitHub private disclosure fallback）仍保持 honest non-blocking posture；它们不是本轮 repo-internal delivery blocker。
