---
phase: 09
status: passed
updated: 2026-03-14
---

# Phase 09 UAT

## Automated UAT Verdict

- ✅ Protocol root 只暴露显式 contract；implicit delegation 已移除。
- ✅ Root/core/config-flow/MQTT package 不再重新导出 legacy protocol root names。
- ✅ `Coordinator.devices` 为 read-only mapping，无法经 public surface 直接改写 runtime registry。
- ✅ outlet power 写入与读取统一走 `LiproDevice.outlet_power_info` formal primitive；diagnostics / sensor 已同步收口。

## Evidence

- `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_public_surface_guards.py tests/core/test_outlet_power.py tests/test_coordinator_public.py tests/platforms/test_sensor.py tests/core/test_diagnostics.py`

## Follow-up Residuals

- `custom_components.lipro.core.api.LiproClient` explicit compat shell
- `custom_components/lipro/core/protocol/facade.py::LiproProtocolFacade.get_device_list` compat wrapper
- `custom_components/lipro/core/protocol/facade.py::LiproMqttFacade.raw_client` explicit seam
