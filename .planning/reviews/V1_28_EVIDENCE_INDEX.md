# v1.28 Evidence Index

**Purpose:** 为 `v1.28 Governance Portability, Verification Stratification & Open-Source Continuity Hardening` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 governance truth portability、verification stratification、docs-first continuity wording 与 milestone closeout / archive handoff 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-28

## Pull Contract

- 本文件只索引正式真源、promoted phase closeout bundle、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续任何新 milestone 都必须从这里 pull `v1.28` 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.28-MILESTONE-AUDIT.md` 是 `v1.28` 的 verdict home；`.planning/milestones/v1.28-ROADMAP.md` 与 `.planning/milestones/v1.28-REQUIREMENTS.md` 只保留历史快照，不反向定义未来 active story。
- `Phase 102` 的 closeout bundle 已通过 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 成为长期治理 / CI evidence；`v1.28` closeout 后，archived-only route truth 固定为 `no active milestone route / latest archived baseline = v1.28`，后续下一条正式路线只能通过 `$gsd-new-milestone` 建立。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Governance truth portability / gsd fast-path smoke | `.planning/phases/102-governance-portability-verification-stratification-and-open-source-continuity-hardening/{102-01-SUMMARY.md,102-VERIFICATION.md,102-VALIDATION.md}`, `tests/meta/{governance_current_truth.py,test_governance_bootstrap_smoke.py,test_governance_route_handoff_smoke.py,governance_followup_route_current_milestones.py,test_phase102_governance_portability_guards.py}` | `.planning/phases/102-*`, `tests/meta/` | `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase102_governance_portability_guards.py` | `102` | archived-only route contract、portable fast-path proof 与 focused latest-archived guard 已收口为同一条治理真相 |
| Verification stratification / docs-first continuity wording | `.planning/phases/102-governance-portability-verification-stratification-and-open-source-continuity-hardening/{102-02-SUMMARY.md,102-VERIFICATION.md}`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/codebase/README.md`, `docs/{README.md,TROUBLESHOOTING.md,MAINTAINER_RELEASE_RUNBOOK.md}` | `.planning/baseline/`, `.planning/codebase/`, `docs/` | `uv run pytest -q tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/toolchain_truth_docs_fast_path.py && uv run python scripts/check_markdown_links.py` | `102` | current archived-only truth 与 historical closeout reference 已明确分层；public first hop 与 maintainer appendix 继续讲同一条 docs-first 故事 |
| Milestone closeout / latest archived handoff | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/v1.28-MILESTONE-AUDIT.md`, `.planning/reviews/V1_28_EVIDENCE_INDEX.md`, `.planning/milestones/{v1.28-ROADMAP.md,v1.28-REQUIREMENTS.md}` | `.planning/`, `docs/`, `tests/meta/`, `.planning/milestones/` | `uv run pytest -q tests/meta && uv run python scripts/check_file_matrix.py --check` | `102 / milestone closeout` | governance route truth 已翻转为 archived-only baseline `v1.28`，下一步只能经 `$gsd-new-milestone` 建立新 current route |

## Promoted Closeout Bundles

- `Phase 102` promoted bundle: `.planning/phases/102-governance-portability-verification-stratification-and-open-source-continuity-hardening/{102-01-SUMMARY.md,102-02-SUMMARY.md,102-03-SUMMARY.md,102-VERIFICATION.md,102-VALIDATION.md}`

## Milestone Closeout Bundle

- Milestone audit: `.planning/v1.28-MILESTONE-AUDIT.md`
- Evidence index: `.planning/reviews/V1_28_EVIDENCE_INDEX.md`
- Archived roadmap snapshot: `.planning/milestones/v1.28-ROADMAP.md`
- Archived requirements snapshot: `.planning/milestones/v1.28-REQUIREMENTS.md`
- Promoted allowlist home: `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- Archived closeout route truth: `no active milestone route / latest archived baseline = v1.28`

## Carry-Forward Notes

- `maintainer / delegate continuity` 仍是组织治理层风险；它已诚实登记为 next-milestone carry-forward，而不是 `v1.28` blocker。
- `v1.27` 及更早 milestone 的 archived evidence 继续只承担 pull-only baseline 身份；`v1.28` closeout 不反向改写它们的 verdict home。
