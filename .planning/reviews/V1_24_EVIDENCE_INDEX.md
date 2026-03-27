# v1.24 Evidence Index

**Purpose:** 为 `v1.24 Runtime Boundary Tightening, Tooling Kernel Decoupling & Open-Source Entry Convergence` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 runtime boundary tightening、runtime single-wiring convergence、tooling kernel decoupling、docs-first open-source entry / governance-route sync，以及 milestone closeout / archive promotion 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-27

## Pull Contract

- 本文件只索引正式真源、promoted phase closeout bundle、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续任何新 milestone 都必须从这里 pull `v1.24` 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.24-MILESTONE-AUDIT.md` 是 `v1.24` 的 verdict home；`.planning/milestones/v1.24-ROADMAP.md` 与 `.planning/milestones/v1.24-REQUIREMENTS.md` 只保留历史快照，不反向定义未来 active story。
- `Phase 89` 的 closeout bundle 已通过 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 成为长期治理 / CI evidence；在 `v1.24` closeout 当时，archived-only route truth 固定为 `no active milestone route / latest archived baseline = v1.24`，后续下一条正式路线只能通过 `$gsd-new-milestone` 建立。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Runtime boundary tightening / entity-facing verb contract | `custom_components/lipro/runtime_types.py`, `custom_components/lipro/entities/{base.py,firmware_update.py}`, `.planning/phases/89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence/{89-01-SUMMARY.md,89-VERIFICATION.md,89-VALIDATION.md}` | production homes, `tests/meta/`, `.planning/phases/89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence/` | `uv run pytest -q tests/core/coordinator/test_entity_protocol.py tests/meta/public_surface_runtime_contracts.py tests/platforms/test_entity_base.py tests/platforms/test_update_entity_refresh.py tests/platforms/test_firmware_update_entity_edges.py tests/meta/test_phase89_runtime_boundary_guards.py` | `89-01` | entity-facing runtime surface 已冻结为命名 verbs，不再向实体层暴露 service/lock internals |
| Runtime single-wiring convergence / bootstrap artifact ownership | `custom_components/lipro/core/coordinator/{coordinator.py,orchestrator.py,runtime_wiring.py,factory.py}`, `.planning/phases/89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence/{89-02-SUMMARY.md,89-VERIFICATION.md,89-VALIDATION.md}` | production homes, `tests/meta/`, `.planning/phases/89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence/` | `uv run pytest -q tests/core/coordinator/test_runtime_root.py tests/core/test_init_runtime_bootstrap.py tests/core/test_coordinator.py tests/meta/test_phase89_runtime_wiring_guards.py` | `89-02` | runtime bootstrap 现只剩一条 formal wiring story；support services 由 bootstrap artifact 显式持有 |
| Tooling kernel decoupling / script-owned helper home | `scripts/{check_architecture_policy.py,check_file_matrix.py}`, `scripts/lib/{architecture_policy.py,ast_guard_utils.py}`, `.planning/phases/89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence/{89-03-SUMMARY.md,89-VERIFICATION.md,89-VALIDATION.md}` | `scripts/`, `scripts/lib/`, `tests/meta/`, `.planning/phases/89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence/` | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/public_surface_architecture_policy.py tests/meta/test_governance_release_contract.py tests/meta/test_dependency_guards.py tests/meta/toolchain_truth_testing_governance.py tests/meta/test_phase89_tooling_decoupling_guards.py` | `89-03` | governance CLI roots 现统一消费 script-owned helper kernels / sibling modules，不再借 `tests.helpers` 或 ad-hoc `sys.path` 注入完成导入 |
| Docs-first open-source entry / governance-route sync | `README.md`, `README_zh.md`, `docs/README.md`, `.github/ISSUE_TEMPLATE/{bug.yml,feature_request.yml,config.yml}`, `custom_components/lipro/manifest.json`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/phases/89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence/{89-04-SUMMARY.md,89-VERIFICATION.md,89-VALIDATION.md}` | `.planning/`, `docs/`, `.github/`, `tests/meta/`, `.planning/phases/89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence/` | `uv run pytest -q tests/meta/test_version_sync.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase89_entry_route_guards.py` | `89-04` | docs / templates / metadata 与 governance-route truth 已共同收口到 docs-first public entry 与 archived-only handoff story |
| Milestone closeout / archive promotion / latest archived handoff | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/baseline/{AUTHORITY_MATRIX.md,PUBLIC_SURFACES.md,VERIFICATION_MATRIX.md}`, `docs/{developer_architecture.md,MAINTAINER_RELEASE_RUNBOOK.md}`, `.planning/v1.24-MILESTONE-AUDIT.md`, `.planning/reviews/V1_24_EVIDENCE_INDEX.md` | `.planning/`, `docs/`, `tests/meta/`, `.planning/milestones/` | `uv run ruff check . && uv run mypy && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta` | `89 / milestone closeout` | current governance truth 已翻转到 archived-only，latest archived pointer 已提升到 `.planning/reviews/V1_24_EVIDENCE_INDEX.md` |

## Promoted Closeout Bundles

- `Phase 89` promoted bundle: `.planning/phases/89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence/{89-01-SUMMARY.md,89-02-SUMMARY.md,89-03-SUMMARY.md,89-04-SUMMARY.md,89-VERIFICATION.md,89-VALIDATION.md}`

## Archive Promotion Outputs

- Milestone audit: `.planning/v1.24-MILESTONE-AUDIT.md`
- Evidence index: `.planning/reviews/V1_24_EVIDENCE_INDEX.md`
- Archived roadmap snapshot: `.planning/milestones/v1.24-ROADMAP.md`
- Archived requirements snapshot: `.planning/milestones/v1.24-REQUIREMENTS.md`

## Cross-Surface Integration

- planning governance-route contract family 现共同承认 `active_milestone = null`、latest archived baseline = `v1.24`、previous archived baseline = `v1.23` 与 `default next = $gsd-new-milestone`。
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 现只指向 `.planning/reviews/V1_24_EVIDENCE_INDEX.md` 与 `.planning/v1.24-MILESTONE-AUDIT.md` 作为 latest archived pointer / verdict home。
- `docs/developer_architecture.md`、`PUBLIC_SURFACES.md`、`AUTHORITY_MATRIX.md` 与 `VERIFICATION_MATRIX.md` 已共同冻结 `v1.24` archive promotion 后的 archived-only route truth。
- `tests/meta/governance_current_truth.py`、`tests/meta/governance_followup_route_current_milestones.py`、`tests/meta/governance_milestone_archives_truth.py`、`tests/meta/governance_milestone_archives_assets.py`、`tests/meta/test_governance_bootstrap_smoke.py`、`tests/meta/test_governance_route_handoff_smoke.py` 与 `tests/meta/test_governance_promoted_phase_assets.py` 共同守卫 latest archived pointer、promoted evidence 与 handoff route 不回退。
