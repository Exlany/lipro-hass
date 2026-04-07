"""Tests for the extracted MQTT message processor."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock

from custom_components.lipro.core.mqtt import payload as payload_module
from custom_components.lipro.core.mqtt.message_processor import (
    MqttMessageProcessor,
    decode_payload_text,
)

_FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "protocol_boundary"


def _load_fixture(name: str) -> dict[str, object]:
    return cast(
        "dict[str, object]",
        json.loads((_FIXTURE_DIR / name).read_text(encoding="utf-8")),
    )


def _message(topic: str, payload: object) -> MagicMock:
    message = MagicMock()
    message.topic = topic
    message.payload = payload
    return message


def test_decode_payload_text_returns_string_for_valid_text() -> None:
    assert decode_payload_text("{}", "dev1") == "{}"


def test_decode_payload_text_returns_none_for_unexpected_type() -> None:
    assert decode_payload_text(123, "dev1") is None


def test_message_processor_logs_invalid_topic_without_leaking_topic(caplog) -> None:
    processor = MqttMessageProcessor("biz001")
    message = _message("invalid", b'{"light": {"powerState": "1"}}')

    with caplog.at_level(logging.DEBUG):
        outcome = processor.process_message(
            message,
            parse_payload=lambda payload: payload,
            on_message=None,
            invoke_callback=lambda *_args: True,
            set_last_error=lambda err: None,
            clear_last_error=lambda: None,
        )

    assert "Invalid topic format (count=1, len=7), skipping message" in caplog.text
    assert "topic=invalid" not in caplog.text
    assert outcome.kind == "skipped"
    assert outcome.reason_code == "invalid_topic"


def test_message_processor_returns_empty_payload_outcome() -> None:
    processor = MqttMessageProcessor("biz001")

    outcome = processor.process_message(
        _message("Topic_Device_State/biz001/03ab5ccd7cxxxxxx", b""),
        parse_payload=lambda payload: payload,
        on_message=None,
        invoke_callback=lambda *_args: True,
        set_last_error=lambda err: None,
        clear_last_error=lambda: None,
    )

    assert outcome.kind == "skipped"
    assert outcome.reason_code == "empty_payload"


def test_message_processor_returns_payload_unavailable_for_unexpected_raw_payload() -> None:
    processor = MqttMessageProcessor("biz001")

    outcome = processor.process_message(
        _message("Topic_Device_State/biz001/03ab5ccd7cxxxxxx", object()),
        parse_payload=lambda payload: payload,
        on_message=None,
        invoke_callback=lambda *_args: True,
        set_last_error=lambda err: None,
        clear_last_error=lambda: None,
    )

    assert outcome.kind == "skipped"
    assert outcome.reason_code == "payload_unavailable"


def test_message_processor_returns_unexpected_payload_type_outcome() -> None:
    processor = MqttMessageProcessor("biz001")

    outcome = processor.process_message(
        _message("Topic_Device_State/biz001/03ab5ccd7cxxxxxx", b"[]"),
        parse_payload=lambda payload: payload,
        on_message=None,
        invoke_callback=lambda *_args: True,
        set_last_error=lambda err: None,
        clear_last_error=lambda: None,
    )

    assert outcome.kind == "skipped"
    assert outcome.reason_code == "unexpected_payload_type"


def test_message_processor_forwards_valid_properties() -> None:
    processor = MqttMessageProcessor("biz001")
    message = _message(
        "Topic_Device_State/biz001/03ab5ccd7cxxxxxx",
        b'{"light": {"powerState": "1"}}',
    )
    on_message = MagicMock()

    outcome = processor.process_message(
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
    assert outcome.kind == "success"
    assert outcome.reason_code == "processed"


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
    message = _message(topic, json.dumps(payload).encode("utf-8"))
    on_message = MagicMock()

    outcome = processor.process_message(
        message,
        parse_payload=payload_module.parse_mqtt_payload,
        on_message=on_message,
        invoke_callback=lambda callback, _name, *args: (callback(*args), True)[1],
        set_last_error=lambda err: None,
        clear_last_error=lambda: None,
    )

    on_message.assert_called_once_with(device_id, canonical)
    assert outcome.kind == "success"
    assert outcome.reason_code == "processed"


def test_message_processor_returns_empty_properties_outcome() -> None:
    processor = MqttMessageProcessor("biz001")
    clear_last_error = MagicMock()

    outcome = processor.process_message(
        _message("Topic_Device_State/biz001/03ab5ccd7cxxxxxx", b'{"light": {"powerState": "1"}}'),
        parse_payload=lambda _payload: {},
        on_message=MagicMock(),
        invoke_callback=lambda *_args: True,
        set_last_error=lambda err: None,
        clear_last_error=clear_last_error,
    )

    clear_last_error.assert_called_once_with()
    assert outcome.kind == "skipped"
    assert outcome.reason_code == "empty_properties"


def test_message_processor_returns_callback_failed_outcome() -> None:
    processor = MqttMessageProcessor("biz001")
    message = _message(
        "Topic_Device_State/biz001/03ab5ccd7cxxxxxx",
        b'{"light": {"powerState": "1"}}',
    )

    outcome = processor.process_message(
        message,
        parse_payload=lambda _payload: {"powerState": "1"},
        on_message=MagicMock(),
        invoke_callback=lambda *_args: False,
        set_last_error=lambda err: None,
        clear_last_error=lambda: None,
    )

    assert outcome.kind == "failed"
    assert outcome.reason_code == "callback_failed"


def test_message_processor_returns_payload_decode_error_and_sets_last_error() -> None:
    processor = MqttMessageProcessor("biz001")
    captured: list[Exception] = []

    outcome = processor.process_message(
        _message("Topic_Device_State/biz001/03ab5ccd7cxxxxxx", b"{"),
        parse_payload=lambda payload: payload,
        on_message=None,
        invoke_callback=lambda *_args: True,
        set_last_error=captured.append,
        clear_last_error=lambda: None,
    )

    assert len(captured) == 1
    assert captured[0].__class__.__name__ == "JSONDecodeError"
    assert outcome.kind == "failed"
    assert outcome.reason_code == "payload_decode_error"


def test_message_processor_returns_message_processing_error_for_parse_failures() -> None:
    processor = MqttMessageProcessor("biz001")
    captured: list[Exception] = []

    def _raise_value_error(_payload: object) -> dict[str, object]:
        msg = "bad payload"
        raise ValueError(msg)

    outcome = processor.process_message(
        _message("Topic_Device_State/biz001/03ab5ccd7cxxxxxx", b'{"light": {"powerState": "1"}}'),
        parse_payload=_raise_value_error,
        on_message=None,
        invoke_callback=lambda *_args: True,
        set_last_error=captured.append,
        clear_last_error=lambda: None,
    )

    assert len(captured) == 1
    assert isinstance(captured[0], ValueError)
    assert outcome.kind == "failed"
    assert outcome.reason_code == "message_processing_error"
