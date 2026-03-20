# Phase 43 Research

**Date:** 2026-03-20
**Status:** Final
**Plans / Waves:** 4 plans / 4 waves

## What The Review Confirmed

- `custom_components/lipro/services/maintenance.py` 仍直接导入 `control.runtime_access.iter_runtime_entry_coordinators()` 并遍历 coordinator 执行 refresh，说明 service helper 仍承载 runtime traversal，而不是只做 service adapter；
- `custom_components/lipro/services/device_lookup.py` 继续依赖 `control.runtime_access.find_runtime_device_and_coordinator()`，表明 `control/` 已是 runtime truth home，但 `services/` 仍通过 helper 方式侧向消费 control-owned contract；
- `custom_components/lipro/control/runtime_access.py` 已承担 entry traversal、device lookup、telemetry exporter、system-health snapshot coercion、`MagicMock` ghost 防护等多类职责，typed read-model 方向正确，但 public contract 仍偏宽、偏反射；
- `tests/core/test_diagnostics.py`、`tests/core/test_system_health.py`、`tests/services/test_maintenance.py`、`tests/services/test_device_lookup.py` 仍大量依赖 `SimpleNamespace` / `MagicMock` / `entry.runtime_data` 形状，说明 runtime consumer 仍未完全锁定稳定 typed contract；
- `custom_components/lipro/control/entry_lifecycle_controller.py` 已拥有 reload、listener、shutdown、entry setup/unload orchestration，是 `services/maintenance.py` 中 runtime infra 逻辑最自然的 formal home 候选。

## Risk Notes

- 若直接把 `RuntimeAccess` 从宽松反射式读取改成强约束 typed contract，容易一次性打碎 diagnostics / system health / services 现有测试夹具；
- control/services 解耦必须沿既有正式 seams 收口，不能为了解偶而新造 manager、registry、adapter root 或第二条 runtime story；
- `maintenance.py` 的 runtime traversal 若迁移不彻底，仓库会留下“service surface 在 docs 中被 demote、在实现里仍掌握 runtime truth”的双重现实；
- 如果只重构代码而不同时更新 baseline / review docs / meta guards，治理层会继续默许旧边界叙事，导致回归很快重新长回。

## Chosen Strategy

1. 先盘点 `control/` ↔ `services/` 的正式依赖方向，锁定哪些 helper 仍在反向泄露 runtime truth；
2. 再把 `RuntimeAccess` 收敛为稳定 typed read-model：优先服务 diagnostics、system health、maintenance 与 lookup 的显式消费面，而不是继续合法化 `MagicMock` / 私有字段读取；
3. 然后把 `services/maintenance.py` 中的 runtime infra、reload/listener/coordinator traversal 迁回 `EntryLifecycleController` / `runtime_infra` 等既有 formal homes，仅保留 service declaration / adapter helper 身份；
4. 最后同步 docs、review ledgers 与 focused guards，让 control/runtime/service 边界、typed consumer contract 与 service ownership 讲同一条故事。

## Validation Focus

- `uv run pytest tests/core/test_control_plane.py tests/core/test_diagnostics.py tests/core/test_system_health.py -q`
- `uv run pytest tests/services/test_maintenance.py tests/services/test_device_lookup.py tests/services/test_services_registry.py -q`
- `uv run pytest tests/core/test_init.py tests/core/test_init_service_handlers.py tests/core/test_init_entry_forwarding.py -q`
- `uv run pytest tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_phase_history.py tests/meta/test_toolchain_truth.py -q`
