"""Tests for the extracted MQTT message processor."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock

from custom_components.lipro.core.mqtt import payload as payload_module
from custom_components.lipro.core.mqtt.message_processor import (
    MqttMessageProcessor,
    decode_payload_text,
)

_FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "protocol_boundary"


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads((_FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_decode_payload_text_returns_string_for_valid_text() -> None:
    assert decode_payload_text("{}", "dev1") == "{}"


def test_decode_payload_text_returns_none_for_unexpected_type() -> None:
    assert decode_payload_text(123, "dev1") is None


def test_message_processor_logs_invalid_topic_without_leaking_topic(caplog) -> None:
    processor = MqttMessageProcessor("biz001")
    message = MagicMock()
    message.topic = "invalid"
    message.payload = b'{"light": {"powerState": "1"}}'

    with caplog.at_level(logging.DEBUG):
        processor.process_message(
            message,
            parse_payload=lambda payload: payload,
            on_message=None,
            invoke_callback=lambda *_args: True,
            set_last_error=lambda err: None,
            clear_last_error=lambda: None,
        )

    assert "Invalid topic format (count=1, len=7), skipping message" in caplog.text
    assert "topic=invalid" not in caplog.text


def test_message_processor_forwards_valid_properties() -> None:
    processor = MqttMessageProcessor("biz001")
    message = MagicMock()
    message.topic = "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"
    message.payload = b'{"light": {"powerState": "1"}}'
    on_message = MagicMock()

    processor.process_message(
        message,
        parse_payload=lambda _payload: {"powerState": "1"},
        on_message=on_message,
        invoke_callback=lambda callback, _name, *args: (callback(*args), True)[1],
        set_last_error=lambda err: None,
        clear_last_error=lambda: None,
    )

    on_message.assert_called_once_with(
        "03ab5ccd7cxxxxxx",
        {"powerState": "1"},
    )


def test_message_processor_accepts_protocol_boundary_fixture() -> None:
    fixture = _load_fixture("mqtt_properties.device_state.v1.json")
    topic = fixture["topic"]
    payload = fixture["payload"]
    device_id = fixture["device_id"]
    canonical = fixture["canonical"]

    assert isinstance(topic, str)
    assert isinstance(payload, dict)
    assert isinstance(device_id, str)
    assert isinstance(canonical, dict)

    processor = MqttMessageProcessor("biz001")
    message = MagicMock()
    message.topic = topic
    message.payload = json.dumps(payload).encode("utf-8")
    on_message = MagicMock()

    processor.process_message(
        message,
        parse_payload=payload_module.parse_mqtt_payload,
        on_message=on_message,
        invoke_callback=lambda callback, _name, *args: (callback(*args), True)[1],
        set_last_error=lambda err: None,
        clear_last_error=lambda: None,
    )

    on_message.assert_called_once_with(device_id, canonical)
