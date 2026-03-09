"""Tests for the extracted MQTT message processor."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

from custom_components.lipro.core.mqtt.message_processor import (
    MqttMessageProcessor,
    decode_payload_text,
)


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
