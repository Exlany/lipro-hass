"""Tests for Lipro MQTT transport."""

from __future__ import annotations

from custom_components.lipro.core.mqtt.payload import (
    _sanitize_mqtt_log_value,
    parse_mqtt_payload,
)


class TestMqttLogSanitization:
    """Tests for MQTT payload log sanitization."""

    def test_sanitize_list_payload(self):
        """List payloads should be sanitized recursively."""
        payload = [{"accessToken": "secret-token"}, {"nested": {"ip": "192.168.0.2"}}]

        sanitized = _sanitize_mqtt_log_value(payload)

        assert isinstance(sanitized, list)
        assert sanitized[0]["accessToken"] == "***"
        assert sanitized[1]["nested"]["ip"] == "***"

    def test_sanitize_json_string_payload(self):
        """JSON string payloads should be parsed and sanitized."""
        raw = '{"accessToken":"secret-token","nested":{"mac":"AA:BB:CC:DD:EE:FF"}}'

        sanitized = _sanitize_mqtt_log_value(raw)

        assert isinstance(sanitized, str)
        assert "secret-token" not in sanitized
        assert "AA:BB:CC:DD:EE:FF" not in sanitized
        assert "***" in sanitized

    def test_sanitize_non_string_value_passthrough(self):
        """Non-container, non-string values should pass through unchanged."""
        assert _sanitize_mqtt_log_value(42) == 42


class TestParseMqttPayload:
    """Tests for MQTT payload parsing."""

    def test_parse_light_payload(self):
        """Test parsing light device payload."""
        payload = {
            "common": {
                "connectState": "1",
            },
            "light": {
                "powerState": "1",
                "brightness": "80",
                "temperature": "4000",
            },
        }

        result = parse_mqtt_payload(payload)

        assert result["connectState"] == "1"
        assert result["powerState"] == "1"
        assert result["brightness"] == "80"
        assert result["temperature"] == "4000"

    def test_parse_fan_light_payload(self):
        """Test parsing fan light payload with key mapping."""
        payload = {
            "fanLight": {
                "fanOnOff": "1",  # MQTT uses fanOnOff
                "fanGear": "5",
                "fanMode": "1",
            },
        }

        result = parse_mqtt_payload(payload)

        # Should be mapped to REST API key
        assert result["fanOnoff"] == "1"  # REST uses fanOnoff
        assert result["fanGear"] == "5"
        assert result["fanMode"] == "1"

    def test_parse_curtain_payload(self):
        """Test parsing curtain payload with key mapping."""
        payload = {
            "curtain": {
                "progress": "50",  # MQTT uses progress
                "state": "1",  # MQTT uses state
            },
        }

        result = parse_mqtt_payload(payload)

        # Should be mapped to REST API keys
        assert result["position"] == "50"  # REST uses position
        assert result["moving"] == "1"  # REST uses moving

    def test_parse_empty_payload(self):
        """Test parsing empty payload."""
        result = parse_mqtt_payload({})

        assert result == {}

    def test_parse_payload_wrapper_fallback(self):
        """Wrapper payloads should fall back to nested data/payload dicts."""
        result = parse_mqtt_payload({"data": {"light": {"powerState": "1"}}})
        assert result["powerState"] == "1"

        nested = parse_mqtt_payload({"payload": {"common": {"connectState": "1"}}})
        assert nested["connectState"] == "1"

    def test_parse_non_dict_payload(self):
        """Test parsing payload safely ignores non-dict JSON types."""
        assert parse_mqtt_payload([]) == {}
        assert parse_mqtt_payload("not-an-object") == {}
        assert parse_mqtt_payload(None) == {}

    def test_parse_payload_with_unknown_groups(self):
        """Test parsing payload ignores unknown groups."""
        payload = {
            "unknown_group": {
                "key": "value",
            },
            "light": {
                "powerState": "1",
            },
        }

        result = parse_mqtt_payload(payload)

        assert "key" not in result
        assert result["powerState"] == "1"

    def test_parse_payload_with_non_dict_group(self):
        """Test parsing payload handles non-dict groups."""
        payload = {
            "light": "not_a_dict",
            "common": {
                "connectState": "1",
            },
        }

        result = parse_mqtt_payload(payload)

        assert result == {"connectState": "1"}

    def test_parse_real_light_payload(self):
        """Test parsing real MQTT payload captured from Lipro 20X1 light.

        This payload was captured from a real device after POWER_ON command.
        Noise values like "-1" and "" should be filtered out.
        """
        payload = {
            "common": {
                "connectState": "1",
                "deviceInfo": '{"wifi_ssid":"Tide IoT","wifi_rssi":-80}',
                "devicePhysicalMode": "light",
                "latestSyncTimestamp": "1770854728432",
                "version": "11.2.54",
            },
            "light": {
                "beepSwitch": "-1",
                "brightness": "50",
                "brightnessDecimal": "-1",
                "fadeState": "1",
                "gearList": '[{"temperature":0,"brightness":50}]',
                "ldrAutoSwitch": "-1",
                "powerState": "1",
                "seatSwitch": "-1",
                "temperature": "30",
                "upperLed": "",
            },
        }

        result = parse_mqtt_payload(payload)

        # Real values should be present
        assert result["connectState"] == "1"
        assert result["powerState"] == "1"
        assert result["brightness"] == "50"
        assert result["temperature"] == "30"
        assert result["fadeState"] == "1"
        assert result["version"] == "11.2.54"
        assert result["devicePhysicalMode"] == "light"

        # Noise values ("-1" and "") should be filtered out
        assert "beepSwitch" not in result
        assert "brightnessDecimal" not in result
        assert "ldrAutoSwitch" not in result
        assert "seatSwitch" not in result
        assert "upperLed" not in result

    def test_parse_payload_filters_numeric_and_whitespace_noise_values(self):
        """Noise values can be numeric -1 or strings with extra whitespace."""
        payload = {
            "common": {
                "connectState": 1,
            },
            "light": {
                "beepSwitch": -1,
                "seatSwitch": " -1 ",
                "upperLed": " ",
                "powerState": "1",
            },
        }

        result = parse_mqtt_payload(payload)

        assert result["connectState"] == 1
        assert result["powerState"] == "1"
        assert "beepSwitch" not in result
        assert "seatSwitch" not in result
        assert "upperLed" not in result

    def test_parse_payload_preserves_zero_values(self):
        """Test that "0" values are NOT filtered (they are valid states)."""
        payload = {
            "light": {
                "powerState": "0",  # Off — valid
                "brightness": "0",  # Min brightness — valid
            },
        }

        result = parse_mqtt_payload(payload)

        assert result["powerState"] == "0"
        assert result["brightness"] == "0"
