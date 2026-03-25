# v1.20 Evidence Index

**Purpose:** 为 `v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 bootstrap / lifecycle / runtime-access convergence、service-family/helper/runtime-surface formalization、auth residual retirement，以及 archive-truth closure 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-25

## Pull Contract

- 本文件只索引正式真源、promoted phase closeout bundles、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续任何新 milestone 都必须从这里 pull `v1.20` 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.20-MILESTONE-AUDIT.md` 是 `v1.20` 的 verdict home；`.planning/milestones/v1.20-ROADMAP.md` 与 `.planning/milestones/v1.20-REQUIREMENTS.md` 只保留历史快照，不反向定义未来 active story。
- `Phase 72 / 73 / 74` 的 audited closeout bundles 已通过 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 成为长期治理 / CI evidence；`Phase 75` 只承担 archive-truth closure / access-mode honesty 的 execution-trace 身份，不单独提升为 promoted phase bundle。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Runtime bootstrap / lifecycle / runtime-access convergence | `custom_components/lipro/core/coordinator/{coordinator.py,orchestrator.py}`, `custom_components/lipro/control/{entry_root_wiring.py,entry_lifecycle_controller.py,entry_lifecycle_support.py,runtime_access.py}`, `custom_components/lipro/runtime_infra.py`, `72-01..04-SUMMARY.md` | `custom_components/lipro/core/coordinator/`, `custom_components/lipro/control/`, `custom_components/lipro/`, `.planning/phases/72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement/` | `uv run pytest -q tests/core/test_control_plane.py tests/core/test_init.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_unload_reload.py tests/core/test_init_service_handlers.py tests/meta/test_phase72_runtime_bootstrap_route_guards.py` | `72` | bootstrap / lifecycle / runtime-access 只做 inward convergence，不新增 builder folklore、shadow bootstrap chain 或 runtime backdoor |
| Service-family / diagnostics-helper / runtime-surface formalization | `custom_components/lipro/{diagnostics.py,system_health.py}`, `custom_components/lipro/control/{diagnostics_surface.py,system_health_surface.py}`, `custom_components/lipro/services/service_router.py`, `custom_components/lipro/services/schedule.py`, `custom_components/lipro/entities/entity.py`, `73-01..04-SUMMARY.md` | `custom_components/lipro/control/`, `custom_components/lipro/services/`, `custom_components/lipro/entities/`, `.planning/phases/73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization/` | `uv run pytest -q tests/core/test_diagnostics.py tests/core/test_system_health.py tests/services/test_services_registry.py tests/services/test_service_resilience.py tests/platforms/test_entity.py tests/meta/test_governance_promoted_phase_assets.py` | `73` | helper / forwarding chains 已压回 formal service/runtime homes，不恢复 helper-owned public surface |
| Auth residual retirement / suite topicization / governance cleanup | `custom_components/lipro/{entry_auth.py,flow/options_flow.py}`, `tests/meta/test_phase74_cleanup_closeout_guards.py`, `74-01..04-SUMMARY.md`, `74-VERIFICATION.md` | `custom_components/lipro/`, `tests/meta/`, `.planning/phases/74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout/` | `uv run pytest -q tests/flows/test_options_flow.py tests/flows/test_options_flow_utils.py tests/meta/test_phase74_cleanup_closeout_guards.py tests/meta/test_governance_closeout_guards.py` | `74` | auth compat shell 已继续退役，topicized guards 与 cleanup contracts 成为 archive-ready closeout 的正式支撑 |
| Archive truth closure / access-mode honesty | `.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md,MILESTONES.md,v1.20-MILESTONE-AUDIT.md}`, `.planning/reviews/{PROMOTED_PHASE_ASSETS.md,V1_20_EVIDENCE_INDEX.md}`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `.github/ISSUE_TEMPLATE/{bug.yml,config.yml,feature_request.yml}`, `custom_components/lipro/{manifest.json,diagnostics.py,system_health.py}`, `tests/meta/{governance_current_truth.py,governance_followup_route_current_milestones.py,test_governance_milestone_archives.py,test_governance_release_contract.py,test_phase75_governance_closeout_guards.py,test_version_sync.py}` | `.planning/`, `.planning/reviews/`, `docs/`, `.github/`, `tests/meta/` | `uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_phase75_governance_closeout_guards.py tests/meta/test_version_sync.py` | `75 / milestone closeout` | live docs / tests / runbook 已切到 `no active milestone route / latest archived baseline = v1.20`；Phase 75 traces 继续保持 execution-trace only |

## Promoted Closeout Bundles

- `Phase 72` promoted bundle: `.planning/phases/72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement/{72-01-SUMMARY.md,72-02-SUMMARY.md,72-03-SUMMARY.md,72-04-SUMMARY.md,72-VERIFICATION.md,72-VALIDATION.md}`
- `Phase 73` promoted bundle: `.planning/phases/73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization/{73-01-SUMMARY.md,73-02-SUMMARY.md,73-03-SUMMARY.md,73-04-SUMMARY.md,73-VERIFICATION.md,73-VALIDATION.md}`
- `Phase 74` promoted bundle: `.planning/phases/74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout/{74-01-SUMMARY.md,74-02-SUMMARY.md,74-03-SUMMARY.md,74-04-SUMMARY.md,74-VERIFICATION.md,74-VALIDATION.md}`
- `Phase 75` execution traces remain local to `.planning/phases/75-access-mode-truth-closure-evidence-promotion-formalization-and-thin-adapter-typing-hardening/{75-01-SUMMARY.md,75-02-SUMMARY.md,75-03-SUMMARY.md,75-04-SUMMARY.md,75-VERIFICATION.md,75-VALIDATION.md}` and are not promoted.

## Release / Closeout Pull Boundary

- latest archive-ready closeout pointer 现已提升到 `.planning/reviews/V1_20_EVIDENCE_INDEX.md`；`v1.19` 退为 previous archived baseline。
- `archived / evidence-ready` 判断以 `.planning/v1.20-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起。
- 当前治理状态为 `no active milestone route / latest archived baseline = v1.20`；下一条正式路线必须通过 `$gsd-new-milestone` 显式建立，而不是把 `Phase 75` execution truth 回写成新的 active route。
