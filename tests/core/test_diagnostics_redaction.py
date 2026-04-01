"""Tests for diagnostics redaction helpers and redact-key sets."""

from __future__ import annotations

import json

from custom_components.lipro.control.diagnostics_surface import (
    DiagnosticsPayload,
    DiagnosticsValue,
)
from custom_components.lipro.core.utils.redaction import (
    EXPLICIT_SENSITIVE_KEY_VARIANTS,
    PROPERTY_REDACTION_KEY_VARIANTS,
)
from custom_components.lipro.diagnostics import (
    PROPERTY_KEYS_TO_REDACT,
    TO_REDACT,
    _redact_device_properties,
)


def _diag_payload(value: DiagnosticsValue) -> DiagnosticsPayload:
    assert isinstance(value, dict)
    return value


def _diag_list(value: DiagnosticsValue) -> list[DiagnosticsValue]:
    assert isinstance(value, list)
    return value


def _diag_str(value: DiagnosticsValue) -> str:
    assert isinstance(value, str)
    return value


class TestRedactDeviceProperties:
    """Tests for _redact_device_properties."""

    def test_redact_mac(self):
        props = {"mac": "5C:CD:7C:XX:XX:XX", "powerState": "1"}
        result = _redact_device_properties(props)
        assert result["mac"] == "**REDACTED**"
        assert result["powerState"] == "1"

    def test_redact_mac_address(self):
        props = {"macAddress": "5C:CD:7C:XX:XX:XX"}
        result = _redact_device_properties(props)
        assert result["macAddress"] == "**REDACTED**"

    def test_redact_ip(self):
        props = {"ip": "192.168.1.100"}
        result = _redact_device_properties(props)
        assert result["ip"] == "**REDACTED**"

    def test_redact_ip_address(self):
        props = {"ipAddress": "192.168.1.100"}
        result = _redact_device_properties(props)
        assert result["ipAddress"] == "**REDACTED**"

    def test_non_sensitive_preserved(self):
        props = {
            "powerState": "1",
            "brightness": "80",
            "temperature": "4000",
        }
        result = _redact_device_properties(props)
        assert result == props

    def test_redact_wifi_ssid_camel_case(self):
        props = {"wifiSsid": "HomeWiFi-5G"}
        result = _redact_device_properties(props)
        assert result["wifiSsid"] == "**REDACTED**"

    def test_empty_properties(self):
        result = _redact_device_properties({})
        assert result == {}

    def test_case_insensitive_redaction(self):
        props = {"MAC": "5C:CD:7C:XX:XX:XX", "IP": "192.168.1.1"}
        result = _redact_device_properties(props)
        assert result["MAC"] == "**REDACTED**"
        assert result["IP"] == "**REDACTED**"

    def test_redact_nested_structures_and_json_string(self):
        props = {
            "deviceInfo": (
                '{"wifi_ssid":"MyWiFi","ip":"192.168.1.2",'
                '"meta":{"iotDeviceId":"03ab5ccd7c123456"}}'
            ),
            "nested": {
                "gatewayDeviceId": "03ab5ccd7c999999",
                "list": [{"serial": "03ab5ccd7caaaaaa"}],
            },
            "plain": "ok",
        }
        result = _redact_device_properties(props)

        parsed_info = json.loads(_diag_str(result["deviceInfo"]))
        nested = _diag_payload(result["nested"])
        nested_list = _diag_list(nested["list"])
        first_nested = _diag_payload(nested_list[0])
        assert parsed_info["wifi_ssid"] == "**REDACTED**"
        assert parsed_info["ip"] == "**REDACTED**"
        assert parsed_info["meta"]["iotDeviceId"] == "**REDACTED**"
        assert nested["gatewayDeviceId"] == "**REDACTED**"
        assert first_nested["serial"] == "**REDACTED**"
        assert result["plain"] == "ok"

    def test_redact_literal_identifier_values(self):
        props = {
            "note_ip": "10.0.0.8",
            "note_mac": "AA:BB:CC:DD:EE:FF",
            "note_device": "03ab5ccd7c123456",
            "note_device_upper": "03AB5CCD7CABCDEF",
            "safe": "hello",
        }
        result = _redact_device_properties(props)

        assert result["note_ip"] == "**REDACTED**"
        assert result["note_mac"] == "**REDACTED**"
        assert result["note_device"] == "**REDACTED**"
        assert result["note_device_upper"] == "**REDACTED**"
        assert result["safe"] == "hello"

    def test_redact_embedded_identifier_values(self):
        props = {
            "note_ip": "peer=10.0.0.8 retry=1",
            "note_mac": "src=AA:BB:CC:DD:EE:FF dst=11:22:33:44:55:66",
            "note_device": "target=03AB5CCD7CABCDEF changed",
            "safe": "hello world",
        }
        result = _redact_device_properties(props)

        note_ip = _diag_str(result["note_ip"])
        note_mac = _diag_str(result["note_mac"])
        note_device = _diag_str(result["note_device"])
        assert "10.0.0.8" not in note_ip
        assert "AA:BB:CC:DD:EE:FF" not in note_mac
        assert "11:22:33:44:55:66" not in note_mac
        assert "03AB5CCD7CABCDEF" not in note_device
        assert "**REDACTED**" in note_ip
        assert "**REDACTED**" in note_mac
        assert "**REDACTED**" in note_device
        assert result["safe"] == "hello world"

    def test_invalid_json_string_fallback_redaction(self):
        props = {
            "deviceInfo": "{bad json ip=10.0.0.8 mac=AA:BB:CC:DD:EE:FF}",
        }
        result = _redact_device_properties(props)

        device_info = _diag_str(result["deviceInfo"])
        assert "10.0.0.8" not in device_info
        assert "AA:BB:CC:DD:EE:FF" not in device_info
        assert device_info.count("**REDACTED**") == 2

    def test_unknown_secret_like_key_fails_closed(self):
        props = {
            "customSecretToken": "super-secret-token",
            "powerState": "1",
        }
        result = _redact_device_properties(props)

        assert result["customSecretToken"] == "**REDACTED**"
        assert result["powerState"] == "1"

    def test_secret_like_string_fragments_are_redacted(self):
        props = {
            "note": "Authorization: Bearer abcdefghijklmnopqrstuvwxyz0123456789 and apiSecret=shh",
        }
        result = _redact_device_properties(props)

        note = _diag_str(result["note"])
        assert "abcdefghijklmnopqrstuvwxyz0123456789" not in note
        assert "shh" not in note
        assert "**REDACTED**" in note


class TestToRedactKeys:
    """Tests for TO_REDACT set completeness."""

    def test_contains_auth_keys(self):
        assert "password" in TO_REDACT
        assert "password_hash" in TO_REDACT
        assert "access_token" in TO_REDACT
        assert "refresh_token" in TO_REDACT
        assert "user_id" in TO_REDACT

    def test_contains_device_id_keys(self):
        assert "serial" in TO_REDACT
        assert "device_id" in TO_REDACT
        assert "deviceId" in TO_REDACT
        assert "groupId" in TO_REDACT
        assert "iotName" in TO_REDACT
        assert "gatewayDeviceId" in TO_REDACT

    def test_contains_user_keys(self):
        assert "phone" in TO_REDACT
        assert "phone_id" in TO_REDACT


class TestPropertyKeysToRedact:
    """Tests for PROPERTY_KEYS_TO_REDACT set completeness."""

    def test_contains_network_keys(self):
        assert "mac" in PROPERTY_KEYS_TO_REDACT
        assert "macAddress" in PROPERTY_KEYS_TO_REDACT
        assert "ip" in PROPERTY_KEYS_TO_REDACT
        assert "ipAddress" in PROPERTY_KEYS_TO_REDACT

    def test_count(self):
        assert len(PROPERTY_KEYS_TO_REDACT) == 7

class TestSharedRedactionRegistries:
    """Tests for shared diagnostics/share redaction registries."""

    def test_top_level_redaction_keys_follow_shared_registry(self):
        assert set(EXPLICIT_SENSITIVE_KEY_VARIANTS) == TO_REDACT

    def test_property_redaction_keys_follow_shared_registry(self):
        assert set(PROPERTY_REDACTION_KEY_VARIANTS) == PROPERTY_KEYS_TO_REDACT

