"""Tests for AnonymousShareManager."""

from __future__ import annotations

import json
from unittest.mock import patch

from custom_components.lipro.core.anonymous_share.sanitize import (
    _MAX_DICT_ITEMS,
    _MAX_NESTED_DEPTH,
    _MAX_STRING_LENGTH,
    REDACT_KEYS,
    looks_sensitive,
    sanitize_properties,
    sanitize_string,
    sanitize_value,
)
from custom_components.lipro.core.utils.redaction import EXPLICIT_SENSITIVE_KEY_VARIANTS

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class TestLooksSensitive:
    """Tests for looks_sensitive detection."""

    def test_mac_address_detected(self):
        assert looks_sensitive("5C:CD:7C:AA:BB:CC") is True

    def test_mac_address_with_dashes_detected(self):
        assert looks_sensitive("5C-CD-7C-AA-BB-CC") is True

    def test_ip_address_detected(self):
        assert looks_sensitive("192.168.1.100") is True

    def test_ipv6_address_detected(self):
        assert looks_sensitive("fe80::1") is True

    def test_device_id_detected(self):
        assert looks_sensitive("03ab5ccd7c123456") is True

    def test_device_id_uppercase_detected(self):
        assert looks_sensitive("03AB5CCD7CABCDEF") is True

    def test_compact_mac_detected(self):
        assert looks_sensitive("5ccd7c5985f1") is True

    def test_numeric_compact_mac_detected(self):
        assert looks_sensitive("001122334455") is True

    def test_token_like_detected(self):
        token = "qwertyuiopasdfghjklzxcvbnmqwerty"
        assert looks_sensitive(token) is True

    def test_low_entropy_repeated_string_not_sensitive(self):
        assert looks_sensitive("x" * 64) is False

    def test_long_mixed_token_detected(self):
        token = "abcDEF012345_-abcDEF012345_-abcDEF"
        assert looks_sensitive(token) is True

    def test_normal_value_not_sensitive(self):
        assert looks_sensitive("hello") is False
        assert looks_sensitive("100") is False
        assert looks_sensitive("powerState") is False

    def test_short_string_not_sensitive(self):
        assert looks_sensitive("1") is False
        assert looks_sensitive("on") is False


# ===========================================================================
# TestSanitizeString
# ===========================================================================


class TestSanitizeString:
    """Tests for sanitize_string replacement logic."""

    def test_replaces_mac_addresses(self):
        result = sanitize_string("device mac is 5C:CD:7C:AA:BB:CC here")
        assert "[MAC]" in result
        assert "5C:CD:7C:AA:BB:CC" not in result

    def test_replaces_ip_addresses(self):
        result = sanitize_string("host at 192.168.1.100 responded")
        assert "[IP]" in result
        assert "192.168.1.100" not in result

    def test_replaces_ipv6_addresses(self):
        result = sanitize_string("host at fe80::1 responded")
        assert "[IP]" in result
        assert "fe80::1" not in result

    def test_replaces_device_ids(self):
        result = sanitize_string("device 03ab5ccd7c123456 offline")
        assert "[DEVICE_ID]" in result
        assert "03ab5ccd7c123456" not in result

    def test_replaces_uppercase_device_ids(self):
        result = sanitize_string("device 03AB5CCD7CABCDEF offline")
        assert "[DEVICE_ID]" in result
        assert "03AB5CCD7CABCDEF" not in result

    def test_replaces_compact_mac(self):
        result = sanitize_string("rc address 5ccd7c5985f1")
        assert "[MAC]" in result
        assert "5ccd7c5985f1" not in result

    def test_replaces_numeric_compact_mac(self):
        result = sanitize_string("rc address 001122334455")
        assert "[MAC]" in result
        assert "001122334455" not in result

    def test_preserves_normal_text(self):
        text = "powerState changed to on"
        assert sanitize_string(text) == text

    def test_replaces_bearer_token_fragments(self):
        text = "request failed Authorization: Bearer abcDEF012345_-abcDEF012345_-abcDEF"
        result = sanitize_string(text)
        assert "Bearer [TOKEN]" in result
        assert "abcDEF012345_-abcDEF012345_-abcDEF" not in result

    def test_replaces_secret_key_value_fragments(self):
        text = "api failed access_token=abcDEF012345_-abcDEF012345_-abcDEF"
        result = sanitize_string(text)
        assert "access_token=[REDACTED]" in result
        assert "abcDEF012345_-abcDEF012345_-abcDEF" not in result

    def test_replaces_embedded_long_token(self):
        text = "payload trace token abcDEF012345_-abcDEF012345_-abcDEF leaked"
        result = sanitize_string(text)
        assert "[TOKEN]" in result
        assert "abcDEF012345_-abcDEF012345_-abcDEF" not in result

    def test_truncates_long_strings(self):
        """_sanitize_string itself does not truncate; _sanitize_value does."""
        # Use a string with spaces so it doesn't match _RE_TOKEN_LIKE
        long_str = "hello world " * ((_MAX_STRING_LENGTH // 12) + 50)
        assert len(long_str) > _MAX_STRING_LENGTH

        # _sanitize_string only does regex replacement, not truncation
        result = sanitize_string(long_str)
        assert len(result) == len(long_str)

        # _sanitize_value truncates long strings
        result_val = sanitize_value(long_str)
        assert "...[truncated]" in result_val
        assert len(result_val) < len(long_str)


# ===========================================================================
# TestSanitizeProperties
# ===========================================================================


class TestSanitizeProperties:
    """Tests for sanitize_properties dict sanitization."""

    def test_redacts_known_keys(self):
        props = {
            "deviceId": "secret-id",
            "device_id": "secret-device",
            "gateway_device_id": "gw-1",
            "mac": "5C:CD:7C:AA:BB:CC",
            "macAddress": "5C:CD:7C:AA:BB:CC",
            "serial": "some-serial",
            "ssid": "HomeWiFi-5G",
            "wifiSsid": "HomeWiFi-5G",
            "powerState": "1",
        }
        result = sanitize_properties(props)
        assert "deviceId" not in result
        assert "device_id" not in result
        assert "gateway_device_id" not in result
        assert "mac" not in result
        assert "macAddress" not in result
        assert "serial" not in result
        assert "ssid" not in result
        assert "wifiSsid" not in result
        assert "powerState" in result
        assert result["powerState"] == "1"

    def test_preserves_safe_properties(self):
        props = {
            "powerState": "1",
            "brightness": 80,
            "temperature": 4000,
        }
        result = sanitize_properties(props)
        assert result["powerState"] == "1"
        assert result["brightness"] == 80
        assert result["temperature"] == 4000

    def test_sanitizes_values_with_embedded_sensitive_data(self):
        props = {
            "info": "5C:CD:7C:AA:BB:CC",  # MAC as a value
        }
        result = sanitize_properties(props)
        # The value looks sensitive (exact MAC match), so it gets redacted
        assert result["info"] == "[redacted]"

    def test_redact_keys_case_insensitive(self):
        props = {"DEVICEID": "secret", "Mac": "aa:bb:cc:dd:ee:ff"}
        result = sanitize_properties(props)
        assert "DEVICEID" not in result
        assert "Mac" not in result

    def test_redacts_variant_sensitive_keys(self):
        props = {
            "accessToken": "abc",
            "refreshToken": "def",
            "installToken": "tok-1",
            "secretKey": "enc-sk",
            "phoneId": "phone-1",
            "user_id": 10001,
            "biz_id": "biz-1",
            "ipAddress": "10.0.0.5",
            "safe": "ok",
        }
        result = sanitize_properties(props)
        assert result == {"safe": "ok"}

    def test_unknown_secret_like_keys_are_dropped(self):
        props = {
            "customSecretToken": "abc",
            "debug_password_value": "pw",
            "safe": "ok",
        }
        result = sanitize_properties(props)

        assert result == {"safe": "ok"}

    def test_iot_name_remains_preserved_under_shared_registry(self):
        props = {
            "iotName": "Living Room Light",
            "deviceId": "secret-id",
        }
        result = sanitize_properties(props)

        assert result == {"iotName": "Living Room Light"}

    def test_share_redaction_keys_follow_shared_registry(self):
        assert REDACT_KEYS == EXPLICIT_SENSITIVE_KEY_VARIANTS

    def test_secret_like_string_fragments_keep_share_markers(self):
        result = sanitize_string(
            "Authorization: Bearer abcdefghijklmnopqrstuvwxyz0123456789 and apiSecret=shh"
        )

        assert "abcdefghijklmnopqrstuvwxyz0123456789" not in result
        assert "shh" not in result
        assert "[TOKEN]" in result
        assert "[REDACTED]" in result

    def test_sanitizes_json_string_payloads_recursively(self):
        props = {
            "deviceInfo": (
                '{"wifi_ssid":"Lany","ip":"10.0.0.153","deviceId":"03AB5CCD7CABCDEF",'
                '"accessToken":"abc","gateway_device_id":"gw-1","secretKey":"enc-sk",'
                '"rc":[{"address":"5ccd7c5985f1","name":"智能控制器"}]}'
            )
        }

        result = sanitize_properties(props)
        parsed = json.loads(result["deviceInfo"])

        assert "wifi_ssid" not in parsed
        assert "ip" not in parsed
        assert "deviceId" not in parsed
        assert "accessToken" not in parsed
        assert "gateway_device_id" not in parsed
        assert "secretKey" not in parsed
        assert parsed["rc"][0]["address"] == "[redacted]"

    def test_sanitize_value_limits_nested_depth(self):
        payload: dict[str, object] = {}
        current: dict[str, object] = payload
        for index in range(_MAX_NESTED_DEPTH + 3):
            next_node: dict[str, object] = {"value": index}
            current["next"] = next_node
            current = next_node

        result = sanitize_value(payload, preserve_structure=True)
        node = result
        for _ in range(_MAX_NESTED_DEPTH):
            assert isinstance(node, dict)
            node = node.get("next")
        assert node == {}

    def test_sanitize_value_limits_dict_items(self):
        payload = {f"k{index}": index for index in range(_MAX_DICT_ITEMS + 20)}
        result = sanitize_value(payload, preserve_structure=True)
        assert isinstance(result, dict)
        assert len(result) == _MAX_DICT_ITEMS

    def test_sanitize_value_non_string_mapping_key_supported(self):
        payload = {123: "ok", "deviceId": "secret-id"}
        result = sanitize_value(payload, preserve_structure=True)
        assert result == {"123": "ok"}

    def test_sanitize_value_invalid_json_string_kept(self):
        raw = '{"deviceId":'
        result = sanitize_value(raw, preserve_structure=True)
        assert result == raw

    def test_sanitize_value_json_non_container_falls_back(self):
        raw = '{"safe":"value"}'
        with patch(
            "custom_components.lipro.core.anonymous_share.sanitize.json.loads",
            return_value="not-a-container",
        ) as mocked_loads:
            result = sanitize_value(raw, preserve_structure=True)
        mocked_loads.assert_called_once_with(raw)
        assert result == raw

    def test_sanitize_value_none_returns_none(self):
        assert sanitize_value(None, preserve_structure=True) is None

    def test_sanitize_value_returns_sanitized_string(self):
        raw = "host at 192.168.1.100 responded"
        result = sanitize_value(raw)
        assert result == "host at [IP] responded"
        assert result != "[redacted]"


# ===========================================================================
# TestRecordDevice
# ===========================================================================
