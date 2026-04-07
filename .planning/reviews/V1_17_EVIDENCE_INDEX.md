# v1.17 Evidence Index

**Purpose:** 为 `v1.17 Residual Formalization, Quality-Balance Hardening & Open-Source Contract Closure` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 runtime read-model formalization、schedule/service de-protocolization、checker/integration balance hardening、honest open-source contract sync 与 milestone archive promotion 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-24

## Pull Contract

- 本文件只索引正式真源、phase summaries / verification、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续任何新 milestone 都必须从这里 pull `v1.17` 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.17-MILESTONE-AUDIT.md` 是 `v1.17` 的 verdict home；`.planning/milestones/v1.17-ROADMAP.md` 与 `.planning/milestones/v1.17-REQUIREMENTS.md` 只保留历史快照，不反向定义未来 active story。
- `69-SUMMARY.md` / `69-VERIFICATION.md` / `69-VALIDATION.md` 共同构成 `Phase 69` 的 closeout evidence；本索引只负责集中 pull 这些已登记资产。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Runtime read-model formalization | `custom_components/lipro/control/{runtime_access.py,runtime_access_support.py}`, `custom_components/lipro/runtime_infra.py`, `69-01-SUMMARY.md`, `69-02-SUMMARY.md` | `custom_components/lipro/control/`, `custom_components/lipro/`, `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/` | `uv run pytest -q tests/meta/test_phase69_support_budget_guards.py tests/core/test_control_plane.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_unload_reload.py tests/services/test_maintenance.py` | `69` | `runtime_access.py` 继续保持唯一 outward runtime home，helper/read-model seam 已 ownerized 到更窄正式结构 |
| Schedule / service de-protocolization | `custom_components/lipro/services/schedule.py`, `custom_components/lipro/core/coordinator/services/protocol_service.py`, `69-03-SUMMARY.md` | `custom_components/lipro/services/`, `custom_components/lipro/core/coordinator/services/` | `uv run pytest -q tests/services/test_services_schedule.py tests/core/test_init_service_handlers_schedules.py tests/core/coordinator/services/test_protocol_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_request_policy.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_topics.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_phase69_support_budget_guards.py` | `69` | service/schedule path 已退回 device-context 与 typed protocol contract，不再维护 protocol-shaped choreography |
| Quality-balance hardening | `scripts/check_*.py`, `tests/meta/test_toolchain_truth.py`, `tests/meta/test_governance_guards.py`, `tests/integration/test_telemetry_exporter_integration.py`, `69-04-SUMMARY.md`, `69-VERIFICATION.md` | `scripts/`, `tests/meta/`, `tests/integration/` | `uv run pytest -q tests/test_refactor_tools.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py tests/integration/test_telemetry_exporter_integration.py tests/services/test_maintenance.py` | `69` | checker coverage、integration depth 与 meta guard 可导航性已被拉回更平衡的门禁组合 |
| Honest open-source contract | `pyproject.toml`, `custom_components/lipro/manifest.json`, `docs/README.md`, `SECURITY.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`, `69-04-SUMMARY.md`, `69-05-SUMMARY.md` | `docs/`, `.planning/`, `tests/meta/` | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py` | `69` | docs / metadata / support / continuity 现共同承认 `v1.17` 已归档且当前无 active milestone route |
| Milestone closeout / archive promotion | `.planning/v1.17-MILESTONE-AUDIT.md`, `.planning/reviews/V1_17_EVIDENCE_INDEX.md`, `.planning/milestones/v1.17-*.md`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` | `.planning/`, `.planning/milestones/`, `.planning/reviews/` | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | `69` | `v1.17` closeout 已完成，latest archive-ready closeout pointer 已提升到 `V1_17_EVIDENCE_INDEX.md` |

## Release / Closeout Pull Boundary

- latest archive-ready closeout pointer 现已提升到 `.planning/reviews/V1_17_EVIDENCE_INDEX.md`；`v1.16` 退为上一条 archive baseline。
- `archived / evidence-ready` 判断以 `.planning/v1.17-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起。
- 当前无 active milestone route；下一条正式路线必须通过 `$gsd-new-milestone` 显式建立，而不是把 `Phase 69` execution truth 回写成新的 current route。
