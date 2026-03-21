# Phase 48 Research

**Date:** 2026-03-21
**Status:** Final
**Plans / Waves:** 4 plans / 3 waves

## What The Review Confirmed

- `custom_components/lipro/control/runtime_access.py` 约 `467` 行，当前按函数簇同时承担 explicit-member coercion、telemetry exporter builder、entry/coordinator traversal、device lookup、system-health snapshot coercion 与 diagnostics projection；方向正确，但已经是 projection-heavy hotspot；
- `custom_components/lipro/core/coordinator/coordinator.py` 约 `444` 行，虽然 service layer、runtime context 与 orchestrator helpers 已存在，但根类仍保留 entity bookkeeping、command failure translation、MQTT setup/shutdown 以及 scheduled update-cycle glue；
- `custom_components/lipro/__init__.py` 约 `417` 行，lazy composition 仍是正确 contract，但 `_entry_auth_module()` / public patch seam wrappers / service registry builder / lifecycle controller builder 让 HA root adapter 视觉密度偏高；
- `custom_components/lipro/control/entry_lifecycle_controller.py` 约 `412` 行，已经是 setup/unload/reload 正式 owner，但 prepare/complete/activate/unload/reload helper 仍集中在单类中，协作者注入与流程桥接密度偏高；
- `custom_components/lipro/control/diagnostics_surface.py` 约 `220` 行，而 `telemetry_surface.py` / `system_health_surface.py` 仅 `65-67` 行，说明 runtime projection 真相并未均匀分布：大量 topic 仍堆在 `runtime_access.py` 中。

## Risk Notes

- 如果把 `RuntimeAccess` topicization 直接做成新的 public helper cluster，容易把“唯一正式 home”重新打散成多入口；
- 如果 `Coordinator` slim-down 只是把方法挪文件但不减少 root decision density，复杂度只是迁移位置，不会形成长期收益；
- `__init__.py` 的任何瘦身都不能破坏 patch seam 与 lazy import 行为，否则会直接回归 `tests/core/test_init*.py` 的关键契约；
- `EntryLifecycleController` 若把 ownership 重新推给 `runtime_infra` 或 services，会回流第二条 lifecycle story；
- guard 与 baseline 若不同步更新，后续重构即便代码正确，也会被旧治理真相重新合法化为漂移。

## Chosen Strategy

1. 先把 `runtime_access.py` 的 topic 按 projection/telemetry/system-health concern 继续 inward，优先缩减 mega-file 感，而不是改变 formal import home；
2. 并行继续下沉 `Coordinator` 的 update-cycle / lifecycle ballast 到现有 `orchestrator.py`、`lifecycle.py` 或 service/runtime collaborators，保持 `Coordinator` 对外 surface 稳定；
3. 在前两步稳定后，再 slim `__init__.py` 与 `EntryLifecycleController` 的 builder / lifecycle glue，确保 lazy wiring 与 single-owner story 不漂移；
4. 最后用 dependency/public-surface/baseline guards 把新的 formal-root story 固化成 machine-checkable current truth。

## Validation Focus

- `uv run pytest tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_control_plane.py -q`
- `uv run pytest tests/core/test_coordinator.py tests/core/test_coordinator_integration.py tests/test_coordinator_public.py tests/test_coordinator_runtime.py -q`
- `uv run pytest tests/core/test_init.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_unload_reload.py tests/core/test_init_runtime_behavior.py tests/core/test_init_service_handlers.py -q`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py -q`
