# v1.16 Evidence Index

**Purpose:** 为 `v1.16 Master Audit Follow-Through, Hotspot Finalization & Docs Contract Hardening` 提供机器友好的 `archived / evidence-ready with carry-forward` closeout 入口，集中索引 refreshed repo-wide audit follow-through、telemetry / MQTT / anonymous-share / OTA / runtime hotspot slimming、docs/release contract hardening 与 repo-wide gate closure 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready with carry-forward`)
**Updated:** 2026-03-24

## Pull Contract

- 本文件只索引正式真源、phase summaries / verification、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续 `v1.17 / Phase 69` 与后续 milestone audit 必须从这里继续 pull 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.16-MILESTONE-AUDIT.md` 是 `v1.16` 的 verdict home；`.planning/milestones/v1.16-ROADMAP.md` 与 `.planning/milestones/v1.16-REQUIREMENTS.md` 只保留历史快照，不反向定义活跃 current story。
- `68-SUMMARY.md` / `68-VERIFICATION.md` / `68-VALIDATION.md` 共同构成 `Phase 68` 的 closeout evidence；本索引只负责集中 pull 这些已登记资产。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Telemetry / MQTT hotspot finalization | `custom_components/lipro/core/telemetry/*`, `custom_components/lipro/core/mqtt/*`, `68-01-SUMMARY.md` | `custom_components/lipro/core/telemetry/`, `custom_components/lipro/core/mqtt/`, `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/` | `uv run pytest -q tests/core/telemetry/test_models.py tests/core/telemetry/test_sinks.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_mqtt_payload.py tests/core/mqtt/test_topics.py tests/meta/test_phase68_hotspot_budget_guards.py` | `68` | telemetry outward contract 与 MQTT staged ingress 继续沿单一 formal home 收口 |
| Anonymous-share / OTA / diagnostics thinning | `custom_components/lipro/core/anonymous_share/*`, `custom_components/lipro/core/api/diagnostics_api_ota.py`, `68-02-SUMMARY.md` | `custom_components/lipro/core/anonymous_share/`, `custom_components/lipro/core/api/`, `custom_components/lipro/services/` | `uv run pytest -q tests/core/test_share_client.py tests/core/test_anonymous_share_storage.py tests/core/test_init_service_handlers_share_reports.py tests/services/test_services_share.py tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_request_policy.py tests/services/test_services_diagnostics.py` | `68` | share token / submit 与 diagnostics query path 已退回更窄 collaborator seams |
| Runtime infra / control-surface slimming | `custom_components/lipro/runtime_infra.py`, `custom_components/lipro/control/runtime_access.py`, `custom_components/lipro/services/maintenance.py`, `68-03-SUMMARY.md` | `custom_components/lipro/`, `custom_components/lipro/control/`, `custom_components/lipro/services/` | `uv run pytest -q tests/services/test_maintenance.py tests/core/test_init.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_unload_reload.py tests/core/test_diagnostics.py tests/core/test_system_health.py` | `68` | runtime/control outward homes 继续保持 thin projection posture，没有长回第二 orchestration root |
| Docs / metadata / governance freeze | `README*`, `docs/README.md`, `custom_components/lipro/manifest.json`, `pyproject.toml`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`, `68-04-SUMMARY.md`, `68-05-SUMMARY.md`, `68-06-SUMMARY.md` | `docs/`, `.planning/`, `tests/meta/` | `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py` | `68` | public first-hop、version/release signal 与 review-fed guards 现在讲同一条 current story |
| Milestone closeout / archive promotion | `.planning/v1.16-MILESTONE-AUDIT.md`, `.planning/reviews/V1_16_EVIDENCE_INDEX.md`, `.planning/milestones/v1.16-*.md`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` | `.planning/`, `.planning/milestones/`, `.planning/reviews/` | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | `68` | `v1.16` closeout 已完成；non-blocking residual 已正式 carry-forward 到 `v1.17 / Phase 69` |

## Release / Closeout Pull Boundary

- latest archive-ready closeout pointer 现已提升到 `.planning/reviews/V1_16_EVIDENCE_INDEX.md`；`v1.15` 退为上一条 archive baseline。
- `archived / evidence-ready with carry-forward` 判断以 `.planning/v1.16-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起。
- `v1.17 / Phase 69` 必须从 `v1.16` 的 archived evidence 与 carry-forward ledger 起步，而不是从 conversation memory 或未登记的 phase workspace 反向拼装故事。
