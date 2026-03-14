---
phase: 03-control-plane-convergence
plan: "02"
status: completed
completed: 2026-03-12
requirements:
  - CTRL-01
  - CTRL-02
  - CTRL-03
  - CTRL-04
---

# Summary 03-02

## Outcome
- 建立 `custom_components/lipro/control/diagnostics_surface.py`、`system_health_surface.py`、`runtime_access.py`、`redaction.py`、`service_router.py`。
- `custom_components/lipro/diagnostics.py` 与 `system_health.py` 现在只保留 HA adapter 职责；support surface 通过 control-owned runtime access 获取状态。
- `services/registrations.py` 切到 `control.service_router` 作为正式 service callback root。

## Verification
- `uv run pytest tests/core/test_diagnostics.py tests/core/test_system_health.py tests/services/test_services_registry.py tests/services/test_execution.py tests/services/test_service_resilience.py tests/services/test_services_diagnostics.py tests/services/test_maintenance.py tests/services/test_services_share.py -q`
