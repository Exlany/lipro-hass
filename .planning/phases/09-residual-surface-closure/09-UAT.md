---
phase: 09
status: passed
updated: 2026-03-14
---

# Phase 09 UAT

## Automated UAT Verdict

- ✅ `09-01` ~ `09-03` 的 production closure verdict 仍成立。
- ✅ `09-04` / `09-05` 已执行完成；legacy tests 已与 production closure 共享同一 formal surface / shared harness / explicit compat seam truth。
- ✅ Protocol root 只暴露显式 contract；implicit delegation 已移除。
- ✅ Root/core/config-flow/MQTT package 不再重新导出 legacy protocol root names。
- ✅ `Coordinator.devices` 为 read-only mapping，无法经 public surface 直接改写 runtime registry。
- ✅ outlet power 写入与读取统一走 `LiproDevice.outlet_power_info` formal primitive；diagnostics / sensor 已同步收口。

## Evidence

- `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_public_surface_guards.py tests/core/test_outlet_power.py tests/test_coordinator_public.py tests/platforms/test_sensor.py tests/core/test_diagnostics.py`
- `uv run pytest -q tests/core/api/test_api.py tests/core/api/test_response_safety.py tests/core/api/test_api_status_endpoints.py tests/core/api/test_api_status_service.py tests/core/api/test_api_status_service_regressions.py tests/core/api/test_helper_modules.py tests/core/api/test_schedule_codec.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_candidate_queries.py tests/core/api/test_api_schedule_candidate_mutations.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_api_command_service.py tests/core/api/test_request_codec.py`
- `uv run pytest -q tests/platforms/test_sensor.py tests/platforms/test_entity_behavior.py tests/platforms/test_platform_entities_behavior.py tests/test_coordinator_public.py tests/integration/test_mqtt_coordinator_integration.py tests/core/test_diagnostics.py tests/core/mqtt/test_mqtt.py`

## Follow-up Residuals

- `custom_components.lipro.core.api.LiproClient` explicit compat shell
- `custom_components/lipro/core/protocol/facade.py::LiproProtocolFacade.get_device_list` compat wrapper
- `custom_components/lipro/core/protocol/facade.py::LiproMqttFacade.raw_client` explicit seam
