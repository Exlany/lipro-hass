# v1.14 Evidence Index

**Purpose:** 为 `v1.14 Governance Truth Realignment, Typed Runtime Access & Final Hidden-Root Closure` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 governance latest-pointer closure、typed runtime access、telemetry/schedule/diagnostics hotspot slimming、runtime-access 去反射化、anonymous-share outcome-native submit contract，以及 release-target fidelity / protocol seam hardening 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-23

## Pull Contract

- 本文件只索引正式真源、phase summaries / verifications、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续 `$gsd-new-milestone`、milestone audit 与 route arbitration 必须从这里继续 pull 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.14-MILESTONE-AUDIT.md` 是 `v1.14` 的 verdict home；`.planning/milestones/v1.14-ROADMAP.md` 与 `.planning/milestones/v1.14-REQUIREMENTS.md` 只保留历史快照，不反向定义活跃 current story。
- `63-SUMMARY.md` / `63-VERIFICATION.md`、`64-SUMMARY.md` / `64-VERIFICATION.md`、`65-SUMMARY.md` / `65-VERIFICATION.md`、`66-SUMMARY.md` / `66-VERIFICATION.md` 是 promoted closeout evidence；`63-66` 缺失 `*-VALIDATION.md` 的事实已经登记到 milestone audit 的 non-blocking tech debt，不由本索引重新裁决。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Governance truth realignment / typed runtime access / hidden-root closure | `PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md`, `MILESTONES.md`, `custom_components/lipro/control/runtime_access.py`, `custom_components/lipro/__init__.py`, `63-VERIFICATION.md` | `.planning/`, `custom_components/lipro/control/`, `.planning/phases/63-governance-truth-realignment-typed-runtime-access-and-hidden-root-closure/` | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_milestone_archives.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py` | `63` | governance pointer、typed runtime read-model 与 hidden-root closure 已被冻结为 archive-ready evidence |
| Telemetry / schedule / diagnostics follow-through | `custom_components/lipro/core/telemetry/*`, `custom_components/lipro/services/schedule.py`, `custom_components/lipro/core/api/diagnostics_api_service.py`, `64-VERIFICATION.md` | `custom_components/lipro/core/telemetry/`, `custom_components/lipro/services/`, `.planning/phases/64-telemetry-typing-schedule-contracts-and-diagnostics-hotspot-slimming/` | `uv run pytest -q tests/services/test_services_schedule.py tests/services/test_services_diagnostics.py tests/meta/test_governance_guards.py` | `64` | telemetry contracts、schedule formal contract 与 diagnostics thin outward home 已完成 closeout freezing |
| Runtime-access de-reflection / device extras / anonymous-share closure | `custom_components/lipro/control/runtime_access_support.py`, `custom_components/lipro/core/device/extras_features.py`, `custom_components/lipro/core/anonymous_share/*`, `65-VERIFICATION.md` | `custom_components/lipro/control/`, `custom_components/lipro/core/device/`, `custom_components/lipro/core/anonymous_share/`, `.planning/phases/65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure/` | `uv run pytest -q tests/core/test_control_plane.py tests/core/anonymous_share/test_manager_submission.py tests/core/test_share_client.py tests/meta/test_governance_guards.py` | `65` | mock-aware reflection、raw sidecar second truth 与 bool-only submit bridge 已退出正式主路径 |
| Release-target fidelity / adapter-root cleanup / focused protocol seams | `.github/workflows/release.yml`, `README.md`, `README_zh.md`, `custom_components/lipro/{__init__.py,sensor.py,select.py}`, `tests/core/api/test_api_transport_executor.py`, `tests/core/protocol/test_facade.py`, `66-VERIFICATION.md` | `.github/workflows/`, repo root docs, `custom_components/lipro/`, `.planning/phases/66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening/` | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py tests/core/api/test_api_transport_executor.py tests/core/coordinator/services/test_protocol_service.py tests/core/protocol/test_facade.py` | `66` | tagged release truth、adapter-root explicit imports 与 focused protocol seam proof 已形成归档基线 |
| Milestone closeout / archive promotion | `.planning/v1.14-MILESTONE-AUDIT.md`, `.planning/reviews/V1_14_EVIDENCE_INDEX.md`, `.planning/milestones/v1.14-*.md`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` | `.planning/`, `.planning/milestones/`, `.planning/reviews/` | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_milestone_archives.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | `63-66` | `v1.14` closeout 已完成；后续里程碑必须从 archived evidence 而非 conversation memory 起步 |

## Release / Closeout Pull Boundary

- latest archive-ready closeout pointer 现已提升到 `.planning/reviews/V1_14_EVIDENCE_INDEX.md`；`v1.13` 退为上一条 archive baseline。
- `archived / evidence-ready` 判断以 `.planning/v1.14-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起。
- `v1.14` archive snapshots 是历史记录，不取代下一轮 `.planning/PROJECT.md` / `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` / `.planning/STATE.md` 的活跃治理角色。
