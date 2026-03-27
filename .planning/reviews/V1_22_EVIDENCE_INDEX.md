# v1.22 Evidence Index

**Purpose:** 为 `v1.22 Maintainer Entry Contracts, Release Operations Closure & Contributor Routing` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 contributor onramp、release-operations closure、community-health intake / stewardship formalization，以及 governance/open-source guard freeze 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-27

## Pull Contract

- 本文件只索引正式真源、promoted phase closeout bundles、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续任何新 milestone 都必须从这里 pull `v1.22` 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.22-MILESTONE-AUDIT.md` 是 `v1.22` 的 verdict home；`.planning/milestones/v1.22-ROADMAP.md` 与 `.planning/milestones/v1.22-REQUIREMENTS.md` 只保留历史快照，不反向定义未来 active story。
- `Phase 81 / 82 / 83 / 84` 的 closeout bundles 已通过 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 成为长期治理 / CI evidence；在 `v1.22` closeout 当时，archived-only route truth 固定为 `no active milestone route / latest archived baseline = v1.22`，后续 active route 必须改由新的 planning governance-route contract family 单独承载。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Contributor onramp / docs-first route convergence | `README.md`, `README_zh.md`, `docs/README.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `SECURITY.md`, `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md` | repo root docs, `docs/`, `.planning/phases/81-contributor-onramp-route-convergence-and-public-entry-contract/` | `uv run pytest -q tests/meta/test_governance_release_docs.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | `81` | public first hop 与 contributor architecture route 已冻结成长期 no-growth concern |
| Release operations closure / archive-evidence chain | `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `CHANGELOG.md`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/v1.22-MILESTONE-AUDIT.md`, `.planning/reviews/V1_22_EVIDENCE_INDEX.md` | `docs/`, `.planning/`, `.planning/phases/82-release-operations-closure-and-evidence-chain-formalization/` | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/test_governance_milestone_archives.py` | `82` | maintainer-facing release route、version-sync triad 与 archive-evidence pointer 已收口成单一 audited release chain |
| Evidence-first intake / stewardship continuity | `.github/ISSUE_TEMPLATE/*.yml`, `.github/pull_request_template.md`, `SUPPORT.md`, `SECURITY.md`, `CONTRIBUTING.md`, `.github/CODEOWNERS` | `.github/`, repo root docs, `.planning/phases/83-intake-templates-and-maintainer-stewardship-contract/` | `uv run pytest -q tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_promoted_phase_assets.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py` | `83` | community-health intake 与 maintainer stewardship 已显式冻结，无 hidden delegate / backup-maintainer folklore |
| Governance/open-source guard freeze / archived-only route transition | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/baseline/{AUTHORITY_MATRIX.md,PUBLIC_SURFACES.md,VERIFICATION_MATRIX.md}`, `.planning/reviews/{FILE_MATRIX.md,RESIDUAL_LEDGER.md,KILL_LIST.md,PROMOTED_PHASE_ASSETS.md}`, `tests/meta/*governance*` | `.planning/`, `tests/meta/`, `.planning/phases/84-governance-open-source-guard-coverage-and-milestone-truth-freeze/` | `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_promoted_phase_assets.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/test_governance_milestone_archives.py tests/meta/test_version_sync.py` | `84` | focused guards 与 ledgers 已把 `Phase 84 complete` closeout-ready truth 顺利前推到 archived-only baseline，不再需要额外 hotfix phase |

## Promoted Closeout Bundles

- `Phase 81` promoted bundle: `.planning/phases/81-contributor-onramp-route-convergence-and-public-entry-contract/{81-01-SUMMARY.md,81-02-SUMMARY.md,81-03-SUMMARY.md,81-SUMMARY.md,81-VERIFICATION.md,81-VALIDATION.md}`
- `Phase 82` promoted bundle: `.planning/phases/82-release-operations-closure-and-evidence-chain-formalization/{82-01-SUMMARY.md,82-02-SUMMARY.md,82-03-SUMMARY.md,82-SUMMARY.md,82-VERIFICATION.md,82-VALIDATION.md}`
- `Phase 83` promoted bundle: `.planning/phases/83-intake-templates-and-maintainer-stewardship-contract/{83-01-SUMMARY.md,83-02-SUMMARY.md,83-03-SUMMARY.md,83-SUMMARY.md,83-VERIFICATION.md,83-VALIDATION.md}`
- `Phase 84` promoted bundle: `.planning/phases/84-governance-open-source-guard-coverage-and-milestone-truth-freeze/{84-01-SUMMARY.md,84-02-SUMMARY.md,84-03-SUMMARY.md,84-SUMMARY.md,84-VERIFICATION.md,84-VALIDATION.md}`

## Release / Closeout Pull Boundary

- latest archive-ready closeout pointer 现已提升到 `.planning/reviews/V1_22_EVIDENCE_INDEX.md`；`v1.21` 退为 previous archived baseline。
- `archived / evidence-ready` 判断以 `.planning/v1.22-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起。
- historical closeout route truth（`v1.22` archive promotion 当时）为 `no active milestone route / latest archived baseline = v1.22`，且下一步通过 `$gsd-new-milestone` 建立新 milestone；当前 active route 不由本索引定义。