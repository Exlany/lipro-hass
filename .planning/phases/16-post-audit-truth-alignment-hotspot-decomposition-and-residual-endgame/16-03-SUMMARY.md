# 16-03 Summary

## Outcome

- Unified control/service payload contracts across `service_router.py`, `device_lookup.py`, `maintenance.py`, `share.py`, and diagnostics helpers so handlers no longer depend on wide `dict[str, Any]` conventions.
- Hardened `runtime_access.py` and `entry_auth.py` around degraded test doubles and legacy token persistence: runtime entry projection now degrades safely, while token persistence prefers `AuthSessionSnapshot` and only falls back to `get_auth_data()` as a narrow compatibility bridge.
- Closed runtime regressions discovered by focused control/diagnostics/system-health tests without reopening a second orchestration story.

## Hotspot Metrics

- `custom_components/lipro/control/service_router.py`: `Any` `15 -> 0`
- `custom_components/lipro/services/device_lookup.py`: `Any` `12 -> 0`
- `custom_components/lipro/services/maintenance.py`: `Any` `7 -> 0`
- `custom_components/lipro/control/runtime_access.py`: kept `Any = 0`, `type: ignore = 0`; added only explicit degraded-entry guards

## Key Files

- `custom_components/lipro/control/service_router.py`
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/services/device_lookup.py`
- `custom_components/lipro/services/maintenance.py`
- `custom_components/lipro/services/share.py`
- `custom_components/lipro/services/diagnostics/helpers.py`
- `custom_components/lipro/services/diagnostics/handlers.py`
- `custom_components/lipro/entry_auth.py`
- `tests/core/test_control_plane.py`
- `tests/core/test_diagnostics.py`
- `tests/core/test_init.py`
- `tests/core/test_system_health.py`
- `tests/services/test_device_lookup.py`
- `tests/services/test_maintenance.py`

## Validation

- `uv run pytest -q tests/core/test_control_plane.py tests/core/test_developer_report.py tests/core/test_diagnostics.py tests/core/test_init.py tests/core/test_system_health.py tests/services/test_execution.py tests/services/test_services_registry.py tests/services/test_service_resilience.py tests/services/test_services_share.py tests/services/test_services_diagnostics.py tests/services/test_device_lookup.py tests/services/test_maintenance.py tests/flows/test_config_flow.py`
- `uv run mypy custom_components/lipro/control/runtime_access.py custom_components/lipro/services/maintenance.py custom_components/lipro/services/device_lookup.py custom_components/lipro/services/share.py custom_components/lipro/services/diagnostics/helpers.py custom_components/lipro/services/diagnostics/handlers.py custom_components/lipro/entry_auth.py`
- `uv run ruff check custom_components/lipro/control custom_components/lipro/services custom_components/lipro/entry_auth.py`
