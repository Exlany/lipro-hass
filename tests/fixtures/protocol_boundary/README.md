# Protocol Boundary Fixture Matrix

## Purpose

This directory stores replay-ready fixtures for protocol-boundary decoder families.

It complements `tests/fixtures/api_contracts/` instead of duplicating it:

- `rest.mqtt-config@v1` continues to use `tests/fixtures/api_contracts/get_mqtt_config.*.json`
- `mqtt.properties@v1` uses the fixture in this directory because it models an inbound MQTT state frame rather than a REST API envelope

## Initial Matrix

| Family | Fixture | Owning Tests | Notes |
|---|---|---|---|
| `rest.mqtt-config@v1` | `../api_contracts/get_mqtt_config.direct.json`, `../api_contracts/get_mqtt_config.wrapped.json` | `tests/core/api/test_protocol_contract_matrix.py` | Reuses existing protocol contract truth; do not duplicate here. |
| `mqtt.properties@v1` | `mqtt_properties.device_state.v1.json` | `tests/core/mqtt/test_mqtt_payload.py`, `tests/core/mqtt/test_message_processor.py` | Replay-ready MQTT state frame fixture carrying topic, payload, canonical output, and fingerprint. |

## Rules

- Each fixture must carry enough metadata for replay and downstream telemetry assertions.
- Canonical output must remain the only truth consumed outside the protocol plane.
- When a family already has a formal authority source elsewhere, this directory must reference it rather than cloning a second truth file.
