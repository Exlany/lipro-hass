# v1.15 Evidence Index

**Purpose:** 为 `v1.15 Typed Contract Convergence, Tooling Kernel Hardening & Mypy Closure` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 telemetry / REST / anonymous-share / service-handler / runtime-control / toolchain-governance typed-contract convergence 与 repo-wide gate closure 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-24

## Pull Contract

- 本文件只索引正式真源、phase summaries / verification、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续 `$gsd-new-milestone`、milestone audit 与 route arbitration 必须从这里继续 pull 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.15-MILESTONE-AUDIT.md` 是 `v1.15` 的 verdict home；`.planning/milestones/v1.15-ROADMAP.md` 与 `.planning/milestones/v1.15-REQUIREMENTS.md` 只保留历史快照，不反向定义活跃 current story。
- `67-SUMMARY.md` / `67-VERIFICATION.md` / `67-VALIDATION.md` 共同构成 `Phase 67` 的 closeout evidence；本索引只负责集中 pull 这些已登记资产。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Telemetry typed-contract convergence | `custom_components/lipro/core/telemetry/*`, `custom_components/lipro/control/runtime_access_support.py`, `custom_components/lipro/control/telemetry_surface.py`, `67-01-SUMMARY.md` | `custom_components/lipro/core/telemetry/`, `custom_components/lipro/control/`, `.planning/phases/67-typed-contract-convergence-toolchain-hardening-and-mypy-closure/` | `uv run pytest -q tests/core/telemetry/test_models.py tests/core/telemetry/test_sinks.py tests/core/telemetry/test_exporter.py` | `67` | telemetry source/view payloads now share one JSON-safe TypedDict truth |
| REST / anonymous-share contract closure | `custom_components/lipro/core/api/*`, `custom_components/lipro/core/anonymous_share/*`, `custom_components/lipro/services/share.py`, `67-02-SUMMARY.md` | `custom_components/lipro/core/api/`, `custom_components/lipro/core/anonymous_share/`, `custom_components/lipro/services/` | `uv run pytest -q tests/core/api/test_api_status_service.py tests/core/api/test_api_transport_executor.py` | `67` | REST/auth/share seams now obey explicit JsonObject / OperationOutcome contracts |
| Service-handler fixtures / runtime-control wiring closure | `tests/conftest.py`, `tests/core/test_init_service_handlers*.py`, `custom_components/lipro/core/coordinator/runtime_context.py`, `custom_components/lipro/core/coordinator/runtime_wiring.py`, `67-03-SUMMARY.md`, `67-04-SUMMARY.md` | `tests/`, `custom_components/lipro/core/coordinator/`, `custom_components/lipro/control/` | `uv run pytest -q tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_debug_queries.py tests/core/test_init_service_handlers_device_resolution.py tests/core/test_init_service_handlers_schedules.py tests/core/test_init_service_handlers_sensor_feedback.py tests/services/test_services_schedule.py tests/core/test_control_plane.py tests/services/test_services_registry.py tests/platforms/test_update_background_tasks.py tests/core/test_init.py` | `67` | typed doubles and honest callables replaced broad object folklore |
| Toolchain / governance freeze | `tests/meta/*`, `docs/README.md`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`, `67-05-SUMMARY.md`, `67-06-SUMMARY.md` | `tests/meta/`, `.planning/`, `docs/` | `uv run pytest -q tests/meta/toolchain_truth_ci_contract.py tests/meta/toolchain_truth_release_contract.py tests/meta/toolchain_truth_python_stack.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_version_sync.py tests/meta/test_blueprints.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_guards.py` | `67` | current-story docs and toolchain guards now agree on the archived v1.15 closeout truth |
| Milestone closeout / archive promotion | `.planning/v1.15-MILESTONE-AUDIT.md`, `.planning/reviews/V1_15_EVIDENCE_INDEX.md`, `.planning/milestones/v1.15-*.md`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` | `.planning/`, `.planning/milestones/`, `.planning/reviews/` | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_milestone_archives.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | `67` | `v1.15` closeout 已完成；后续里程碑必须从 archived evidence 而非 conversation memory 起步 |

## Release / Closeout Pull Boundary

- latest archive-ready closeout pointer 现已提升到 `.planning/reviews/V1_15_EVIDENCE_INDEX.md`；`v1.14` 退为上一条 archive baseline。
- `archived / evidence-ready` 判断以 `.planning/v1.15-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起。
- `v1.15` archive snapshots 是历史记录，不取代下一轮 `.planning/PROJECT.md` / `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` / `.planning/STATE.md` 的活跃治理角色。
