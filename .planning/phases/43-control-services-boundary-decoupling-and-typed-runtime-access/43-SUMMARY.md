---
phase: 43
slug: control-services-boundary-decoupling-and-typed-runtime-access
status: passed
updated: 2026-03-20
---

# Phase 43 Summary

## Outcome

- `43-01`: `custom_components/lipro/control/runtime_access.py` 与 `custom_components/lipro/control/models.py` 已收口成 typed runtime read-model / diagnostics projection contract；`diagnostics_surface.py` 不再混搭 ad-hoc coordinator introspection，并显式拒绝 `MagicMock` ghost runtime 形状。
- `43-02`: `custom_components/lipro/runtime_infra.py` 已收回 device-registry listener、pending reload task cleanup 与 reload coordination ownership；`custom_components/lipro/services/maintenance.py` 降为 `refresh_devices` thin adapter。
- `43-03`: `custom_components/lipro/services/device_lookup.py` 已降为 service-facing target → `device_id` resolver；最终 `(device, coordinator)` bridge 现在由 `custom_components/lipro/control/service_router_support.py` 通过 `RuntimeAccess` 正式持有。
- `43-04`: `docs/developer_architecture.md`、baseline matrices、review ledgers 与 meta guards 已同步到单一 current story：typed `RuntimeAccess`、control-owned device lookup bridge、`runtime_infra` listener ownership，以及 `maintenance` / `device_lookup` 的 helper demotion。

## Validation

- `uv run pytest tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_control_plane.py tests/core/test_init.py tests/core/test_init_service_handlers.py tests/core/test_init_service_handlers_device_resolution.py tests/services/test_device_lookup.py tests/services/test_maintenance.py tests/services/test_services_registry.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_closeout_guards.py -q` → `171 passed`
- `uv run python scripts/check_file_matrix.py --check` → passed
- `uv run python scripts/check_architecture_policy.py --check` → passed
- Focused subplan regressions also passed during execution: `43-02` (`60 passed`), `43-03` (`29 passed`), `43-04` meta/governance gate (`55 passed`).

## Notes

- `43-SUMMARY.md` 与 `43-VERIFICATION.md` 已提升为 promoted phase assets；`43-CONTEXT.md`、`43-RESEARCH.md`、`43-0x-PLAN.md` 与 `43-0x-SUMMARY.md` 继续保持 execution-trace 身份。
- `v1.6` 当前已进入 `Phase 43 complete`；下一步建议 `$gsd-execute-phase 44`，继续治理资产降噪与术语收口。
