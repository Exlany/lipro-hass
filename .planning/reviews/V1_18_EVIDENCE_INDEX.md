# v1.18 Evidence Index

**Purpose:** 为 `v1.18 Support-Seam Slimming, OTA Resolver Consolidation & Governance Test Topicization` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 runtime support helper decomposition、anonymous-share / OTA shared-helper convergence、archive-vs-current truth freeze、governance topicization 与 milestone archive promotion 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-24

## Pull Contract

- 本文件只索引正式真源、phase summaries / verification、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续任何新 milestone 都必须从这里 pull `v1.18` 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.18-MILESTONE-AUDIT.md` 是 `v1.18` 的 verdict home；`.planning/milestones/v1.18-ROADMAP.md` 与 `.planning/milestones/v1.18-REQUIREMENTS.md` 只保留历史快照，不反向定义未来 active story。
- `70-SUMMARY.md` / `70-VERIFICATION.md` / `70-VALIDATION.md` 共同构成 `Phase 70` 的 closeout evidence；本索引只负责集中 pull 这些已登记资产。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Runtime support helper decomposition | `custom_components/lipro/control/{runtime_access.py,runtime_access_support.py,runtime_access_support_members.py,runtime_access_support_telemetry.py,runtime_access_support_views.py,runtime_access_support_devices.py}`, `70-02-SUMMARY.md` | `custom_components/lipro/control/`, `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/` | `uv run pytest -q tests/meta/test_phase69_support_budget_guards.py tests/meta/test_phase70_governance_hotspot_guards.py tests/core/test_control_plane.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/meta/test_dependency_guards.py` | `70` | `runtime_access.py` 继续保持唯一 outward runtime home，support helper family 只承担 inward collaborator 身份 |
| Anonymous-share / OTA helper convergence | `custom_components/lipro/core/anonymous_share/{share_client_flows.py,share_client_ports.py,share_client_refresh.py,share_client_submit.py}`, `custom_components/lipro/core/{api/diagnostics_api_ota.py,ota/query_support.py}`, `custom_components/lipro/entities/firmware_update.py`, `70-03-SUMMARY.md` | `custom_components/lipro/core/anonymous_share/`, `custom_components/lipro/core/ota/`, `custom_components/lipro/entities/` | `uv run pytest -q tests/meta/test_phase68_hotspot_budget_guards.py tests/core/test_share_client.py tests/core/api/test_api_diagnostics_service.py tests/platforms/test_update.py tests/platforms/test_update_entity_refresh.py tests/core/ota/test_ota_rows_cache.py` | `70` | anonymous-share submit/refresh/outcome 与 OTA query/selection 已共享 helper truth，不再保留 entity-local choreography |
| Archive freeze / governance topicization | `tests/meta/{governance_contract_helpers.py,test_phase70_governance_hotspot_guards.py,test_version_sync.py,test_governance_release_contract.py,test_governance_milestone_archives.py,governance_followup_route_current_milestones.py}`, `docs/README.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`, `70-04-SUMMARY.md`, `70-05-SUMMARY.md` | `tests/meta/`, `docs/`, `.planning/` | `uv run pytest -q tests/meta/test_version_sync.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase70_governance_hotspot_guards.py` | `70` | current mutable truth 已冻结到 current docs / runbook / registry；historical phase/evidence assets 不再承担 version sync 职责 |
| Milestone closeout / archive promotion | `.planning/v1.18-MILESTONE-AUDIT.md`, `.planning/reviews/V1_18_EVIDENCE_INDEX.md`, `.planning/milestones/v1.18-*.md`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` | `.planning/`, `.planning/milestones/`, `.planning/reviews/` | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | `70` | `v1.18` closeout 已完成，latest archive-ready closeout pointer 已提升到 `V1_18_EVIDENCE_INDEX.md` |

## Release / Closeout Pull Boundary

- latest archive-ready closeout pointer 现已提升到 `.planning/reviews/V1_18_EVIDENCE_INDEX.md`；`v1.17` 退为上一条 archive baseline。
- `archived / evidence-ready` 判断以 `.planning/v1.18-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起。
- 当前无 active milestone route；下一条正式路线必须通过 `$gsd-new-milestone` 显式建立，而不是把 `Phase 70` execution truth 回写成新的 current route。
