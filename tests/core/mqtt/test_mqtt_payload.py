"""Focused tests for MQTT payload sanitization helpers."""

from __future__ import annotations

import json

from custom_components.lipro.core.mqtt import payload as payload_module


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
