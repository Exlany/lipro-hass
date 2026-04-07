# 20-02 Summary

## Outcome

- Formalized `mqtt.topic@v1` and `mqtt.message-envelope@v1` as explicit MQTT boundary families, keeping `mqtt.properties@v1` focused on canonical property truth only.
- Routed MQTT topic parsing, envelope decoding, and downstream message processing through the same protocol-boundary decoder story rather than scattered helper-local rules.
- Added protocol-boundary fixtures, replay manifests, replay driver dispatch, and focused MQTT regression coverage for all three MQTT family stages.

## Key Files

- `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`
- `custom_components/lipro/core/protocol/boundary/__init__.py`
- `custom_components/lipro/core/mqtt/message_processor.py`
- `custom_components/lipro/core/mqtt/payload.py`
- `tests/fixtures/protocol_boundary/mqtt_topic.device_state.v1.json`
- `tests/fixtures/protocol_boundary/mqtt_message_envelope.device_state.v1.json`
- `tests/fixtures/protocol_replay/mqtt/topic.device_state.v1.replay.json`
- `tests/fixtures/protocol_replay/mqtt/message_envelope.device_state.v1.replay.json`
- `tests/core/mqtt/test_mqtt_payload.py`
- `tests/core/mqtt/test_protocol_replay_mqtt.py`
- `tests/harness/protocol/replay_driver.py`
- `tests/harness/protocol/replay_models.py`

## Validation

- `uv run pytest -q tests/core/mqtt/test_mqtt.py tests/core/mqtt/test_topic_builder.py tests/core/mqtt/test_mqtt_payload.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_transport_refactored.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/meta/test_protocol_replay_assets.py`
- `uv run ruff check custom_components/lipro/core/mqtt/message_processor.py custom_components/lipro/core/mqtt/payload.py custom_components/lipro/core/protocol/boundary/mqtt_decoder.py tests/core/mqtt/test_mqtt_payload.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/harness/protocol/replay_models.py tests/harness/protocol/replay_driver.py tests/integration/test_protocol_replay_harness.py tests/meta/test_protocol_replay_assets.py`
