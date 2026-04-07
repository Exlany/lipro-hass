# 21-02 Summary

## Outcome

- 收窄了 protocol / runtime / control 热点 broad-catch 的 arbitration seam：关键主链现在优先做 cancellation passthrough 与 typed failure recording，而不是无差别吞掉异常。
- `Coordinator._async_update_data()` 现已把 timeout、auth、protocol、unexpected 四类更新失败写入 runtime telemetry；`mqtt_lifecycle`、`mqtt_runtime` 与 protocol façade 相关链路也会记录稳定 failure input。
- 保留的 best-effort seam（如 entry lifecycle abort、diagnostics helpers）现在显式直通 `asyncio.CancelledError`，避免把终止语义误判成普通失败。

## Key Files

- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`
- `custom_components/lipro/core/coordinator/mqtt_lifecycle.py`
- `custom_components/lipro/control/entry_lifecycle_controller.py`
- `custom_components/lipro/services/diagnostics/helpers.py`
- `tests/core/test_init.py`
- `tests/core/test_init_edge_cases.py`
- `tests/core/test_coordinator.py`
- `tests/core/coordinator/runtime/test_mqtt_runtime.py`
- `tests/core/coordinator/services/test_telemetry_service.py`
- `tests/services/test_service_resilience.py`
- `tests/integration/test_mqtt_coordinator_integration.py`

## Validation

- `uv run pytest -q tests/core/test_init.py tests/core/test_init_edge_cases.py tests/core/test_coordinator.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/coordinator/services/test_telemetry_service.py tests/services/test_service_resilience.py tests/integration/test_mqtt_coordinator_integration.py` → `272 passed`
- `uv run mypy custom_components/lipro/core/telemetry/models.py custom_components/lipro/core/telemetry/sinks.py custom_components/lipro/core/protocol/telemetry.py custom_components/lipro/core/protocol/facade.py custom_components/lipro/core/coordinator/services/telemetry_service.py custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py custom_components/lipro/core/coordinator/mqtt_lifecycle.py custom_components/lipro/core/coordinator/coordinator.py custom_components/lipro/control/entry_lifecycle_controller.py custom_components/lipro/services/diagnostics/helpers.py tests/harness/protocol/replay_models.py tests/harness/protocol/replay_driver.py tests/harness/protocol/replay_assertions.py tests/harness/protocol/replay_report.py` → `Success: no issues found in 14 source files`

## Notes

- 本 plan 不是机械清除所有 `except Exception`，而是把关键主链与 best-effort seam 的处理语义分开立契约。
- broad-catch 的残余治理同步与 lifecycle 真相回写，继续留给 `Phase 23` 统一处理，避免 21/22 各写各的话术。
