# Phase 48 Verification

status: passed

## Goal

- 验证 `Phase 48: Runtime-access and formal-root hotspot decomposition without public-surface drift` 是否完成 `RUN-08` / `ARC-06`：`RuntimeAccess`、`Coordinator`、`__init__.py` 与 `EntryLifecycleController` 的热点已继续 inward/topicize，且 public surface、lazy wiring 与 control/runtime boundary 没有漂移。

## Evidence

- `custom_components/lipro/control/runtime_access.py` 现已把 support-only helper cluster 下沉到 `runtime_access_support.py`，但 `build_runtime_snapshot()`、`build_runtime_diagnostics_projection()`、`iter_runtime_entries()` 与 `build_entry_telemetry_exporter()` 仍维持在 formal import home。
- `custom_components/lipro/control/telemetry_surface.py`、`custom_components/lipro/control/system_health_surface.py` 与 `custom_components/lipro/control/diagnostics_surface.py` 继续只消费 formal control helpers；`tests/meta/test_dependency_guards.py` 已显式阻止它们回退到 private support helper 或 `entry.runtime_data`。
- `custom_components/lipro/core/coordinator/coordinator.py` 已把 scheduled update orchestration 下沉到 `custom_components/lipro/core/coordinator/lifecycle.py::CoordinatorUpdateCycle`；`Coordinator` 仍然保留唯一 runtime root 身份与 public import home。
- `custom_components/lipro/__init__.py` 的 entry-auth patch seams 已压成 module-level alias；`custom_components/lipro/control/entry_lifecycle_controller.py` 通过 `_clear_entry_lifecycle_state()` 收束 setup/unload cleanup；`async_setup_entry()`、`async_unload_entry()` 与 `async_reload_entry()` 的 lazy composition / owner story 保持稳定。
- `.planning/baseline/{DEPENDENCY_MATRIX,PUBLIC_SURFACES,VERIFICATION_MATRIX}.md` 与 `.planning/reviews/FILE_MATRIX.md` 已同步承认 `runtime_access_support.py` support-only 身份、`CoordinatorUpdateCycle` internal-only 身份，以及 `Phase 48` 的 runnable proof。

## Validation

- `uv run ruff check custom_components/lipro/__init__.py custom_components/lipro/control/diagnostics_surface.py custom_components/lipro/control/entry_lifecycle_controller.py custom_components/lipro/control/runtime_access.py custom_components/lipro/control/runtime_access_support.py custom_components/lipro/control/system_health_surface.py custom_components/lipro/control/telemetry_surface.py custom_components/lipro/core/coordinator/coordinator.py custom_components/lipro/core/coordinator/lifecycle.py tests/core/test_control_plane.py tests/core/test_coordinator.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py` → `passed`
- `uv run pytest tests/core/test_control_plane.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/meta/test_dependency_guards.py tests/core/test_coordinator.py -q` → `99 passed`
- `uv run pytest tests/core/coordinator/services/test_polling_service.py tests/core/coordinator/services/test_telemetry_service.py tests/core/test_coordinator.py tests/core/test_coordinator_integration.py tests/test_coordinator_public.py tests/test_coordinator_runtime.py -q` → `55 passed`
- `uv run pytest tests/core/test_init.py tests/core/test_init_runtime_behavior.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_setup_entry_failures.py tests/core/test_init_runtime_unload_reload.py tests/core/test_init_runtime_registry_refresh.py tests/core/test_init_service_handlers.py -q` → `68 passed`
- `uv run python scripts/check_file_matrix.py --check` → `passed`
- `uv run pytest tests/core/test_control_plane.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/coordinator/services/test_polling_service.py tests/core/coordinator/services/test_telemetry_service.py tests/core/test_coordinator.py tests/core/test_coordinator_integration.py tests/test_coordinator_public.py tests/test_coordinator_runtime.py tests/core/test_init.py tests/core/test_init_runtime_behavior.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_setup_entry_failures.py tests/core/test_init_runtime_unload_reload.py tests/core/test_init_runtime_registry_refresh.py tests/core/test_init_service_handlers.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py -q` → `218 passed`

## Notes

- `48-SUMMARY.md` / `48-VERIFICATION.md` 已于本轮被提升进 `PROMOTED_PHASE_ASSETS.md`，具备长期治理 / CI closeout evidence 身份；`48-CONTEXT.md`、`48-RESEARCH.md` 与 `48-0x-PLAN.md` 继续保持 execution-trace 身份。
- 下一治理动作应切换到 `Phase 49`：本轮未触碰 mega-test topicization / failure-localization overhaul，也未开始 REST typed-surface reduction。
