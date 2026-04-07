---
phase: 48
status: passed
plans_completed:
  - 48-01
  - 48-02
  - 48-03
  - 48-04
verification: .planning/phases/48-runtime-access-and-formal-root-hotspot-decomposition-without-public-surface-drift/48-VERIFICATION.md
---

# Phase 48 Summary

## Outcome

- `runtime_access.py` 继续保持唯一正式 import home，但把 entry traversal / device lookup / telemetry exporter support 下沉到 `runtime_access_support.py`，控制面消费者仍经正式入口读取 runtime truth。
- `telemetry_surface.py` 不再直贴 private helper 名称；system-health 与 diagnostics 面继续作为薄消费层，未重新散落 `entry.runtime_data` 或 coordinator internals 读取。
- `Coordinator` 把 scheduled update orchestration 继续 inward 到 `CoordinatorUpdateCycle`；runtime root 仍只有 `Coordinator`，未引入第二 orchestration root。
- `custom_components/lipro/__init__.py` 把 entry-auth patch seams 压成 module-level alias，`EntryLifecycleController` 把 lifecycle-state cleanup 收束成单一 helper，lazy composition 与单一 owner story 保持不变。
- baseline / review / meta guards 已同步承认 `runtime_access_support.py` 是 support-only seam、`CoordinatorUpdateCycle` 是 internal collaborator，并把 `Phase 48` runnable proof 收进 machine-checkable truth。

## Changed Surfaces

- Control runtime read-model: `custom_components/lipro/control/runtime_access.py`, `custom_components/lipro/control/runtime_access_support.py`, `custom_components/lipro/control/telemetry_surface.py`, `custom_components/lipro/control/system_health_surface.py`, `custom_components/lipro/control/diagnostics_surface.py`
- Runtime root decomposition: `custom_components/lipro/core/coordinator/coordinator.py`, `custom_components/lipro/core/coordinator/lifecycle.py`
- Root adapter / lifecycle owner: `custom_components/lipro/__init__.py`, `custom_components/lipro/control/entry_lifecycle_controller.py`
- Governance truth: `.planning/baseline/DEPENDENCY_MATRIX.md`, `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/FILE_MATRIX.md`, `.planning/reviews/PROMOTED_PHASE_ASSETS.md`, `.planning/reviews/README.md`
- Verification: `tests/core/test_control_plane.py`, `tests/core/test_coordinator.py`, `tests/meta/test_dependency_guards.py`, `tests/meta/test_public_surface_guards.py`, `tests/meta/test_governance_closeout_guards.py`

## Verification Snapshot

- `uv run ruff check custom_components/lipro/__init__.py custom_components/lipro/control/diagnostics_surface.py custom_components/lipro/control/entry_lifecycle_controller.py custom_components/lipro/control/runtime_access.py custom_components/lipro/control/runtime_access_support.py custom_components/lipro/control/system_health_surface.py custom_components/lipro/control/telemetry_surface.py custom_components/lipro/core/coordinator/coordinator.py custom_components/lipro/core/coordinator/lifecycle.py tests/core/test_control_plane.py tests/core/test_coordinator.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest tests/core/test_control_plane.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/coordinator/services/test_polling_service.py tests/core/coordinator/services/test_telemetry_service.py tests/core/test_coordinator.py tests/core/test_coordinator_integration.py tests/test_coordinator_public.py tests/test_coordinator_runtime.py tests/core/test_init.py tests/core/test_init_runtime_behavior.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_setup_entry_failures.py tests/core/test_init_runtime_unload_reload.py tests/core/test_init_runtime_registry_refresh.py tests/core/test_init_service_handlers.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py -q`

## Deferred to Later Phases

- `Phase 49`: governance mega-guards / runtime megatests / platform megatests topicization 与 failure-localization hardening
- `Phase 50`: REST typed-surface reduction 与 command/result ownership convergence

## Promotion

- `48-SUMMARY.md` 与 `48-VERIFICATION.md` 已登记到 `.planning/reviews/PROMOTED_PHASE_ASSETS.md`，作为 `Phase 48` 的长期 closeout evidence。
- `48-CONTEXT.md`、`48-RESEARCH.md` 与 `48-0x-PLAN.md` 继续保持 execution-trace 身份，不自动升级为长期治理真源。
