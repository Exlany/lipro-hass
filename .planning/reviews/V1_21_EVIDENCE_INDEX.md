# v1.21 Evidence Index

**Purpose:** 为 `v1.21 Governance Bootstrap Truth Hardening & Planning Route Automation` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 bootstrap truth activation、governance guard topicization、route-handoff quality gates、governance-tooling hotspot decomposition，以及 typing closure / final meta-suite topicization 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-27

## Pull Contract

- 本文件只索引正式真源、promoted phase closeout bundles、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续任何新 milestone 都必须从这里 pull `v1.21` 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.21-MILESTONE-AUDIT.md` 是 `v1.21` 的 verdict home；`.planning/milestones/v1.21-ROADMAP.md` 与 `.planning/milestones/v1.21-REQUIREMENTS.md` 只保留历史快照，不反向定义未来 active story。
- `Phase 76 / 77 / 78 / 79 / 80` 的 closeout bundles 已通过 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 成为长期治理 / CI evidence；在 `v1.21` closeout 当时，archived-only route truth 固定为 `no active milestone route / latest archived baseline = v1.21`，后续 active route 必须改由 active planning governance-route contract family 单独承载。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Machine-readable governance-route activation | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `tests/meta/governance_current_truth.py`, `tests/meta/test_governance_route_handoff_smoke.py` | `.planning/`, `tests/meta/`, `.planning/phases/76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation/` | `uv run pytest -q tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py` | `76` | bootstrap selector 已从 prose-order folklore 收口为 dedicated contract block，归档后继续只允许 archived-only route truth |
| Bootstrap smoke / literal-drift freeze | `tests/meta/{test_governance_bootstrap_smoke.py,governance_contract_helpers.py,governance_promoted_assets.py}`, `.planning/reviews/FILE_MATRIX.md`, `.planning/baseline/VERIFICATION_MATRIX.md` | `tests/meta/`, `.planning/reviews/`, `.planning/baseline/`, `.planning/phases/77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction/` | `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_release_contract.py` | `77` | focused bootstrap smoke、shared helpers 与 public-doc-hidden boundary 已冻结成长期 no-growth concern |
| Route-handoff quality gate formalization | `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/{FILE_MATRIX,PROMOTED_PHASE_ASSETS.md,RESIDUAL_LEDGER.md,KILL_LIST.md}`, `tests/meta/test_governance_milestone_archives.py` | `.planning/baseline/`, `.planning/reviews/`, `tests/meta/`, `.planning/phases/78-quality-gate-formalization-route-handoff-ergonomics-and-milestone-closeout-readiness/` | `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | `78` | fast-path smoke、quality gates 与 promoted evidence allowlist 已把 later closeout readiness 写成可重复执行的正式 contract |
| Governance-tooling hotspot decomposition / release topicization | `scripts/check_file_matrix_registry.py`, `scripts/check_file_matrix_validation.py`, `tests/meta/{test_governance_release_contract.py,test_governance_release_docs.py,test_governance_release_continuity.py}` | `scripts/`, `tests/meta/`, `.planning/phases/79-governance-tooling-hotspot-decomposition-and-release-contract-topicization/` | `uv run pytest -q tests/test_refactor_tools.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py` | `79` | registry monolith 已拆成 thin root + focused companions；release-contract truth 已 topicize 成更清晰的 docs / continuity homes |
| Governance typing closure / final meta-suite topicization | `scripts/check_file_matrix_registry.py`, `tests/meta/{governance_followup_route_current_milestones.py,test_governance_release_contract.py,test_governance_closeout_guards.py}`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` | `scripts/`, `tests/meta/`, `.planning/`, `.planning/phases/80-governance-typing-closure-and-final-meta-suite-hotspot-topicization/` | `uv run mypy --follow-imports=silent . && uv run ruff check tests/meta scripts && uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_version_sync.py` | `80` | typed JSON / registry export seams 已诚实收口，remaining giant governance tests 已 topicize，archive promotion 不再需要补 current-story hotfix |

## Promoted Closeout Bundles

- `Phase 76` promoted bundle: `.planning/phases/76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation/{76-01-SUMMARY.md,76-02-SUMMARY.md,76-03-SUMMARY.md,76-VERIFICATION.md,76-VALIDATION.md}`
- `Phase 77` promoted bundle: `.planning/phases/77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction/{77-01-SUMMARY.md,77-02-SUMMARY.md,77-03-SUMMARY.md,77-VERIFICATION.md,77-VALIDATION.md}`
- `Phase 78` promoted bundle: `.planning/phases/78-quality-gate-formalization-route-handoff-ergonomics-and-milestone-closeout-readiness/{78-01-SUMMARY.md,78-02-SUMMARY.md,78-03-SUMMARY.md,78-SUMMARY.md,78-VERIFICATION.md,78-VALIDATION.md}`
- `Phase 79` promoted bundle: `.planning/phases/79-governance-tooling-hotspot-decomposition-and-release-contract-topicization/{79-01-SUMMARY.md,79-02-SUMMARY.md,79-03-SUMMARY.md,79-SUMMARY.md,79-VERIFICATION.md,79-VALIDATION.md}`
- `Phase 80` promoted bundle: `.planning/phases/80-governance-typing-closure-and-final-meta-suite-hotspot-topicization/{80-01-SUMMARY.md,80-02-SUMMARY.md,80-03-SUMMARY.md,80-SUMMARY.md,80-VERIFICATION.md,80-VALIDATION.md}`

## Release / Closeout Pull Boundary

- latest archive-ready closeout pointer 现已提升到 `.planning/reviews/V1_21_EVIDENCE_INDEX.md`；`v1.20` 退为 previous archived baseline。
- `archived / evidence-ready` 判断以 `.planning/v1.21-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起。
- historical closeout route truth（`v1.21` archive promotion 当时）为 `no active milestone route / latest archived baseline = v1.21`，且下一步通过 `$gsd-new-milestone` 建立新 milestone；当前 active route 不由本索引定义。
