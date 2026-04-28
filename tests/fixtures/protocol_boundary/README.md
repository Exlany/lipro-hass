# Protocol Boundary Fixture Matrix

## Purpose

This directory stores replay-ready fixtures for protocol-boundary decoder families.

It complements `tests/fixtures/api_contracts/` instead of duplicating it:

- `rest.mqtt-config@v1` continues to use `tests/fixtures/api_contracts/get_mqtt_config.*.json`
- `mqtt.topic@v1` and `mqtt.message-envelope@v1` use fixtures here because they model inbound MQTT grammar/envelope truth before properties canonicalization
- `mqtt.properties@v1` uses the fixture in this directory because it models an inbound MQTT state frame rather than a REST API envelope

## Current Matrix

| Family | Fixture | Owning Tests | Notes |
|---|---|---|---|
| `rest.mqtt-config@v1` | `../api_contracts/get_mqtt_config.direct.json`, `../api_contracts/get_mqtt_config.wrapped.json` | `tests/core/api/test_protocol_contract_matrix.py` | Reuses existing protocol contract truth; do not duplicate here. |
| `mqtt.topic@v1` | `mqtt_topic.device_state.v1.json` | `tests/core/mqtt/test_mqtt_payload.py`, `tests/core/mqtt/test_protocol_replay_mqtt.py` | Replay-ready MQTT topic grammar fixture carrying normalized biz/device identifiers. |
| `mqtt.message-envelope@v1` | `mqtt_message_envelope.device_state.v1.json` | `tests/core/mqtt/test_mqtt_payload.py`, `tests/core/mqtt/test_protocol_replay_mqtt.py` | Replay-ready MQTT envelope fixture carrying pre-properties canonical mapping. |
| `mqtt.properties@v1` | `mqtt_properties.device_state.v1.json` | `tests/core/mqtt/test_mqtt_payload.py`, `tests/core/mqtt/test_message_processor.py` | Replay-ready MQTT state frame fixture carrying topic, payload, canonical output, and fingerprint. |

## Boundary Continuity Rule

- `mqtt.topic@v1` 与 `mqtt.message-envelope@v1` 属于 live boundary fixture family；一旦 fixture 落地或更新，必须在本目录与 `tests/fixtures/protocol_replay/` 同步出现，而不是继续停留在 `topics.py`、`message_processor.py` 或 `payload.py` 的 helper 叙事里。
- fixture matrix、replay README、baseline authority wording 必须讲同一条 boundary-first story；若仍有未完成 family，应明确写成 pending boundary coverage，而不是继续沿用 phase closeout 口径。

## Rules

- Each fixture must carry enough metadata for replay and downstream telemetry assertions.
- Canonical output must remain the only truth consumed outside the protocol plane.
- When a family already has a formal authority source elsewhere, this directory must reference it rather than cloning a second truth file.
