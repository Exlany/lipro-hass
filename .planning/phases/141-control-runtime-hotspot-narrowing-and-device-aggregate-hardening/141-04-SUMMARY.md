# Plan 141-04 Summary

- `custom_components/lipro/core/device/device.py` 继续保持 explicit aggregate façade；`outlet_power_info`、`mark_mqtt_update()` 与 `has_recent_mqtt_update()` outward API 未改名，但其 bookkeeping 已委托给 `device_runtime.py` 本地 side-car helper。
- `custom_components/lipro/core/device/device_runtime.py` 现承接 MQTT freshness、outlet-power primitive copy/cleanup 与 legacy `extra_data["power_info"]` 清理；getter 也返回 defensive snapshot，避免 caller 反向污染 aggregate state。
- `custom_components/lipro/control/diagnostics_surface.py` 继续只读取 formal primitives（`device.is_connected`、`device.outlet_power_info`），而 `tests/core/device/test_device.py`、`tests/core/test_outlet_power.py`、`tests/platforms/test_sensor.py`、`tests/platforms/test_entity_behavior.py` 等 focused lanes 共同冻结 no-backdoor story。
