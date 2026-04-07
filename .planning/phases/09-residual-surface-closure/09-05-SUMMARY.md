# 09-05 Summary — Runtime / Platform / Integration Test Convergence

## Outcome

- `tests/conftest.py` 的 `_CoordinatorDouble` 新增 `set_devices()`，platform tests 统一回到共享 device store / read-only `devices` view。
- `tests/platforms/test_sensor.py`、`tests/platforms/test_entity_behavior.py`、`tests/platforms/test_platform_entities_behavior.py` 已移除重复的本地 `get_device` wiring，改用共享 coordinator harness。
- `tests/integration/test_mqtt_coordinator_integration.py` 的 `_FakeMqttFacade` 新增 façade-level emit helpers，message/connect/disconnect 测试不再把 `raw_client` 当通用入口。

## Verification

- `uv run ruff check tests/conftest.py tests/platforms/test_sensor.py tests/platforms/test_entity_behavior.py tests/platforms/test_platform_entities_behavior.py tests/integration/test_mqtt_coordinator_integration.py`
- `uv run pytest -q tests/platforms/test_sensor.py tests/platforms/test_entity_behavior.py tests/platforms/test_platform_entities_behavior.py tests/test_coordinator_public.py tests/integration/test_mqtt_coordinator_integration.py tests/core/test_diagnostics.py tests/core/mqtt/test_mqtt.py`
- Result: `193 passed`
