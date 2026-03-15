# 17-03 Summary

## Outcome

- Unified MQTT concrete naming on `MqttTransportClient`; legacy `LiproMqttClient` naming no longer participates in production truth or package-level export stories.
- Kept transport-local tests focused on concrete behavior while shifting cross-layer runtime/integration expectations back to protocol contracts and locality guards.
- Hardened policy-backed no-export bans so concrete transport stays localized to `core/mqtt` and the protocol seam.

## Key Files

- `custom_components/lipro/core/mqtt/mqtt_client.py`
- `custom_components/lipro/core/mqtt/client_runtime.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/protocol/contracts.py`
- `tests/core/mqtt/test_client_refactored.py`
- `tests/core/mqtt/test_mqtt.py`
- `tests/core/coordinator/runtime/test_mqtt_runtime.py`
- `tests/integration/test_mqtt_coordinator_integration.py`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/test_public_surface_guards.py`

## Validation

- `uv run pytest -q tests/core/mqtt tests/core/coordinator/runtime/test_mqtt_runtime.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py`
- `uv run mypy custom_components/lipro/core/mqtt custom_components/lipro/core/protocol`
- `uv run ruff check custom_components/lipro/core/mqtt custom_components/lipro/core/protocol tests/core/mqtt tests/core/coordinator/runtime tests/integration tests/meta`
