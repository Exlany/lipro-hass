"""Focused tests for MQTT payload sanitization helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from custom_components.lipro.core.mqtt import payload as payload_module
from custom_components.lipro.core.protocol.boundary import (
    decode_mqtt_message_envelope_payload,
    decode_mqtt_properties_payload,
    decode_mqtt_topic_payload,
)

_FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "protocol_boundary"


def _load_fixture(name: str) -> dict[str, object]:
    return cast(
        "dict[str, object]",
        json.loads((_FIXTURE_DIR / name).read_text(encoding="utf-8")),
    )


def test_sanitize_malformed_json_string_falls_back_to_plain_text() -> None:
    """Malformed JSON strings should be treated as plain text."""
    raw = '{"foo":bar}'

    sanitized = payload_module._sanitize_mqtt_log_value(raw)

    assert sanitized == raw


def test_sanitize_json_typeerror_falls_back_to_plain_text(monkeypatch) -> None:
    """TypeError from json.loads should be swallowed and continue sanitization."""
    raw = '{"foo":"bar"}'

    def _raise_type_error(_: object) -> object:
        raise TypeError("bad json payload")

    monkeypatch.setattr(json, "loads", _raise_type_error)

    sanitized = payload_module._sanitize_mqtt_log_value(raw)

    assert sanitized == raw


def test_sanitize_malformed_json_with_sensitive_key_is_redacted() -> None:
    """Malformed JSON should still be redacted by string patterns."""
    raw = "{password:no_quote}"

    sanitized = payload_module._sanitize_mqtt_log_value(raw)

    assert "no_quote" not in sanitized
    assert "***" in sanitized


def test_decode_mqtt_properties_payload_returns_boundary_metadata() -> None:
    fixture = _load_fixture("mqtt_properties.device_state.v1.json")
    payload = fixture["payload"]
    canonical = fixture["canonical"]
    fingerprint = fixture["fingerprint"]
    family = fixture["family"]
    version = fixture["version"]

    assert isinstance(payload, dict)
    assert isinstance(canonical, dict)
    assert isinstance(fingerprint, str)
    assert isinstance(family, str)
    assert isinstance(version, str)

    result = decode_mqtt_properties_payload(payload)

    assert result.key.label == f"{family}@{version}"
    assert result.authority == "tests/core/mqtt/test_mqtt.py"
    assert result.fingerprint == fingerprint
    assert result.canonical == canonical


def test_decode_mqtt_topic_payload_returns_boundary_metadata() -> None:
    fixture = _load_fixture("mqtt_topic.device_state.v1.json")
    topic = fixture["topic"]
    expected_biz_id = fixture["expected_biz_id"]

    assert isinstance(topic, str)
    assert expected_biz_id is None or isinstance(expected_biz_id, str)

    result = decode_mqtt_topic_payload(
        topic,
        expected_biz_id=expected_biz_id,
    )

    assert result.key.label == f"{fixture['family']}@{fixture['version']}"
    assert result.authority.endswith("mqtt_topic.device_state.v1.json")
    assert result.fingerprint == fixture["fingerprint"]
    assert result.canonical == fixture["canonical"]


def test_decode_mqtt_message_envelope_payload_returns_boundary_metadata() -> None:
    fixture = _load_fixture("mqtt_message_envelope.device_state.v1.json")

    result = decode_mqtt_message_envelope_payload(fixture["payload"])

    assert result.key.label == f"{fixture['family']}@{fixture['version']}"
    assert result.authority.endswith("mqtt_message_envelope.device_state.v1.json")
    assert result.fingerprint == fixture["fingerprint"]
    assert result.canonical == fixture["canonical"]


def test_parse_mqtt_payload_reuses_protocol_boundary_fixture_contract() -> None:
    fixture = _load_fixture("mqtt_properties.device_state.v1.json")
    payload = fixture["payload"]
    canonical = fixture["canonical"]

    assert isinstance(payload, dict)
    assert isinstance(canonical, dict)
    assert payload_module.parse_mqtt_payload(payload) == canonical
