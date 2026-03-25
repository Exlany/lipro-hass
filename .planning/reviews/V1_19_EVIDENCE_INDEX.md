# v1.19 Evidence Index

**Purpose:** 为 `v1.19 Audit-Driven Final Hotspot Decomposition & Governance Truth Projection` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 hotspot inward decomposition、route-truth freeze、milestone archive promotion 与 latest-archive pull boundary 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-25

## Pull Contract

- 本文件只索引正式真源、phase summaries / verification、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续任何新 milestone 都必须从这里 pull `v1.19` 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.19-MILESTONE-AUDIT.md` 是 `v1.19` 的 verdict home；`.planning/milestones/v1.19-ROADMAP.md` 与 `.planning/milestones/v1.19-REQUIREMENTS.md` 只保留历史快照，不反向定义未来 active story。
- `71-SUMMARY.md` / `71-VERIFICATION.md` / `71-VALIDATION.md` 共同构成 `Phase 71` 的 closeout evidence；本索引只负责集中 pull 这些已登记资产。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| OTA / firmware-install hotspot decomposition | `custom_components/lipro/entities/firmware_update.py`, `custom_components/lipro/core/api/{diagnostics_api_ota.py,diagnostics_api_ota_support.py}`, `71-02-SUMMARY.md` | `custom_components/lipro/entities/`, `custom_components/lipro/core/api/`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/` | `uv run pytest -q tests/core/api/test_api_diagnostics_service.py tests/platforms/test_update.py tests/platforms/test_update_entity_refresh.py tests/platforms/test_update_install_flow.py tests/meta/test_phase71_hotspot_route_guards.py` | `71` | OTA diagnostics / firmware install 只做 inward helper decomposition，不新增 entity-local choreography 或第二条 outward story |
| Anonymous-share / request pacing / command-runtime decomposition | `custom_components/lipro/core/anonymous_share/share_client_submit.py`, `custom_components/lipro/core/api/request_policy_support.py`, `custom_components/lipro/core/coordinator/runtime/command_runtime.py`, `custom_components/lipro/core/command/result_policy.py`, `71-03-SUMMARY.md` | `custom_components/lipro/core/anonymous_share/`, `custom_components/lipro/core/api/`, `custom_components/lipro/core/coordinator/runtime/` | `uv run pytest -q tests/core/test_share_client.py tests/core/api/test_api_request_policy.py tests/core/coordinator/runtime/test_command_runtime.py tests/meta/test_phase71_hotspot_route_guards.py` | `71` | submit / pacing / command verification long flows 已压回更窄 helper homes，typed outcome / pacing contract 继续保持正式真源 |
| Route-truth freeze and archive-pointer projection | `tests/meta/{governance_current_truth.py,test_phase71_hotspot_route_guards.py,test_governance_release_contract.py,test_governance_milestone_archives.py,test_version_sync.py,governance_followup_route_current_milestones.py}`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`, `docs/{README.md,MAINTAINER_RELEASE_RUNBOOK.md}`, `71-04-SUMMARY.md`, `71-05-SUMMARY.md` | `tests/meta/`, `.planning/`, `docs/` | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_governance_milestone_archives.py tests/meta/test_version_sync.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase71_hotspot_route_guards.py` | `71` | current mutable truth 已切到 `no active milestone route / latest archived baseline = v1.19`；`V1_19_EVIDENCE_INDEX.md` 成为唯一 latest pull-only closeout pointer |
| Milestone closeout / archive promotion | `.planning/v1.19-MILESTONE-AUDIT.md`, `.planning/reviews/V1_19_EVIDENCE_INDEX.md`, `.planning/milestones/v1.19-*.md`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` | `.planning/`, `.planning/milestones/`, `.planning/reviews/` | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | `71` | `v1.19` closeout 已完成，当前无 active milestone route；下一条正式路线必须通过 `$gsd-new-milestone` 显式建立 |

## Release / Closeout Pull Boundary

- latest archive-ready closeout pointer 现已提升到 `.planning/reviews/V1_19_EVIDENCE_INDEX.md`；`v1.18` 退为 previous archived baseline。
- `archived / evidence-ready` 判断以 `.planning/v1.19-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起。
- 当前治理状态为 `no active milestone route / latest archived baseline = v1.19`；下一条正式路线必须通过 `$gsd-new-milestone` 显式建立，而不是把 `Phase 71` execution truth 回写成新的 active route。
