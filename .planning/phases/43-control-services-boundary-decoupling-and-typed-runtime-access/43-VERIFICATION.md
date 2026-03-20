# Phase 43 Verification

status: passed

## Goal

- 核验 `Phase 43: Control-services boundary decoupling and typed runtime access` 是否完成 `ARC-04` / `CTRL-10` / `RUN-07`。
- 最终结论：**`Phase 43` 已于 `2026-03-20` 完成；typed `RuntimeAccess`、`maintenance` thin-adapter demotion、control-owned device/coordinator bridge 与 `runtime_infra` listener ownership 已统一收口到单一正式边界故事。**

## Evidence

- `custom_components/lipro/control/runtime_access.py` 与 `custom_components/lipro/control/models.py` 已提供 typed runtime diagnostics projection、entry-scoped runtime lookup 与 `MagicMock` ghost rejection；`custom_components/lipro/control/diagnostics_surface.py` 仅消费 formal projection / helper path。
- `custom_components/lipro/runtime_infra.py` 现在拥有 device-registry listener、pending reload task cleanup 与 reload coordination；`custom_components/lipro/services/maintenance.py` 只保留 `refresh_devices` service adapter。
- `custom_components/lipro/services/device_lookup.py` 只保留 service-facing `device_id` resolution；`custom_components/lipro/control/service_router_support.py` 通过 `RuntimeAccess` 承接最终 `(device, coordinator)` bridge。
- `docs/developer_architecture.md`、`.planning/baseline/{PUBLIC_SURFACES,DEPENDENCY_MATRIX,AUTHORITY_MATRIX,VERIFICATION_MATRIX}.md`、`.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER,KILL_LIST}.md` 与 meta guards 已同步 Phase 43 current truth。
- `uv run pytest tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_control_plane.py tests/core/test_init.py tests/core/test_init_service_handlers.py tests/core/test_init_service_handlers_device_resolution.py tests/services/test_device_lookup.py tests/services/test_maintenance.py tests/services/test_services_registry.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_closeout_guards.py -q` → `171 passed`
- `uv run python scripts/check_file_matrix.py --check` → passed
- `uv run python scripts/check_architecture_policy.py --check` → passed

## Notes

- `Phase 43` 的 completion truth 已回写 `PROJECT.md`、`ROADMAP.md`、`REQUIREMENTS.md` 与 `STATE.md`。
- 下一治理动作应切换到 `$gsd-execute-phase 44`；`Phase 43` 不再保留 planning-ready 身份。
