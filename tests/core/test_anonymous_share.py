"""Tests for AnonymousShareManager."""

from __future__ import annotations

import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.lipro.const.categories import DeviceCategory
from custom_components.lipro.const.properties import (
    PROP_ACTIVATED,
    PROP_AERATION_GEAR,
    PROP_BATTERY,
    PROP_BODY_REACTIVE,
    PROP_BRIGHTNESS,
    PROP_DARK,
    PROP_DOOR_OPEN,
    PROP_FADE_STATE,
    PROP_FAN_GEAR,
    PROP_FAN_MODE,
    PROP_FOCUS_MODE,
    PROP_HEATER_MODE,
    PROP_LIGHT_MODE,
    PROP_POSITION,
    PROP_SLEEP_AID_ENABLE,
    PROP_TEMPERATURE,
    PROP_WAKE_UP_ENABLE,
    PROP_WIND_GEAR,
)
from custom_components.lipro.core import LiproApiError
from custom_components.lipro.core.anonymous_share import manager as manager_module
from custom_components.lipro.core.anonymous_share.capabilities import (
    detect_device_capabilities,
)
from custom_components.lipro.core.anonymous_share.const import (
    MAX_PENDING_DEVICES,
    MAX_PENDING_ERRORS,
    SHARE_API_KEY,
)
from custom_components.lipro.core.anonymous_share.manager import (
    AnonymousShareManager,
    get_anonymous_share_manager,
)
from custom_components.lipro.core.anonymous_share.sanitize import (
    _MAX_DICT_ITEMS,
    _MAX_NESTED_DEPTH,
    _MAX_STRING_LENGTH,
    looks_sensitive,
    sanitize_properties,
    sanitize_string,
    sanitize_value,
)
from custom_components.lipro.core.anonymous_share.share_client import ShareWorkerClient
from custom_components.lipro.core.api import LiproRestFacade
from custom_components.lipro.core.api.observability import (
    record_api_error as record_observed_api_error,
)
from custom_components.lipro.core.capability import CapabilitySnapshot

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_manager(enabled: bool = True) -> AnonymousShareManager:
    """Create an enabled AnonymousShareManager for testing."""
    mgr = AnonymousShareManager()
    if enabled:
        mgr.set_enabled(True, error_reporting=True, installation_id="test-id")
    return mgr


def _make_mock_device(
    *,
    iot_name: str = "lipro_led",
    physical_model: str = "light",
    device_type: int = 1,
    product_id: int = 100,
    is_group: bool = False,
    properties: dict[str, object] | None = None,
    firmware_version: str | None = "1.0.0",
    min_color_temp_kelvin: int = 2700,
    max_color_temp_kelvin: int = 6500,
    gear_list: list[object] | None = None,
    is_light: bool = True,
    is_fan_light: bool = False,
    is_curtain: bool = False,
    is_sensor: bool = False,
    is_heater: bool = False,
    is_switch: bool = False,
    is_outlet: bool = False,
    has_gear_presets: bool = False,
) -> MagicMock:
    """Create a lightweight mock LiproDevice."""
    device = MagicMock()
    device.iot_name = iot_name
    device.physical_model = physical_model
    device.device_type = device_type
    device.product_id = product_id
    device.is_group = is_group
    device.properties = properties or {}
    device.firmware_version = firmware_version
    device.min_color_temp_kelvin = min_color_temp_kelvin
    device.max_color_temp_kelvin = max_color_temp_kelvin
    device.gear_list = gear_list or []
    device.is_light = is_light
    device.is_fan_light = is_fan_light
    device.is_curtain = is_curtain
    device.is_sensor = is_sensor
    device.is_heater = is_heater
    device.is_switch = is_switch
    device.is_outlet = is_outlet
    device.has_gear_presets = has_gear_presets
    device.has_unknown_physical_model = False
    if is_fan_light:
        category = DeviceCategory.FAN_LIGHT
    elif is_curtain:
        category = DeviceCategory.CURTAIN
    elif is_sensor:
        category = DeviceCategory.BODY_SENSOR
    elif is_heater:
        category = DeviceCategory.HEATER
    elif is_outlet:
        category = DeviceCategory.OUTLET
    elif is_switch:
        category = DeviceCategory.SWITCH
    elif physical_model == "gateway":
        category = DeviceCategory.GATEWAY
    else:
        category = DeviceCategory.LIGHT if is_light else DeviceCategory.UNKNOWN
    device.capabilities = CapabilitySnapshot(
        device_type_hex=f"ff{device_type:06x}",
        category=category,
        platforms=(),
        supports_color_temp=min_color_temp_kelvin > 0 and max_color_temp_kelvin > 0,
        min_color_temp_kelvin=min_color_temp_kelvin,
        max_color_temp_kelvin=max_color_temp_kelvin,
    )
    device.category = MagicMock()
    device.category.value = "light"
    return device


# ===========================================================================
# TestLooksSensitive
# ===========================================================================


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
        token = "a" * 32
        assert looks_sensitive(token) is True

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


class TestRecordDevice:
    """Tests for record_device and record_devices."""

    def test_record_single_device(self):
        mgr = _make_manager()
        device = _make_mock_device(iot_name="lipro_led")
        mgr.record_device(device)
        devices_count, _ = mgr.pending_count
        assert devices_count == 1

    def test_record_multiple_devices(self):
        mgr = _make_manager()
        d1 = _make_mock_device(iot_name="lipro_led")
        d2 = _make_mock_device(iot_name="lipro_fan_light")
        mgr.record_devices([d1, d2])
        devices_count, _ = mgr.pending_count
        assert devices_count == 2

    def test_deduplication(self):
        mgr = _make_manager()
        device = _make_mock_device(iot_name="lipro_led")
        mgr.record_device(device)
        mgr.record_device(device)
        devices_count, _ = mgr.pending_count
        assert devices_count == 1

    def test_disabled_manager_ignores_devices(self):
        mgr = _make_manager(enabled=False)
        device = _make_mock_device()
        mgr.record_device(device)
        devices_count, _ = mgr.pending_count
        assert devices_count == 0

    def test_already_reported_device_skipped(self):
        mgr = _make_manager()
        mgr._reported_device_keys.add("lipro_led")
        device = _make_mock_device(iot_name="lipro_led")
        mgr.record_device(device)
        devices_count, _ = mgr.pending_count
        assert devices_count == 0


# ===========================================================================
# TestRecordError
# ===========================================================================


class TestRecordError:
    """Tests for error recording methods."""

    def test_record_api_error(self):
        mgr = _make_manager()
        mgr.record_api_error(
            endpoint="/api/devices",
            code=500,
            message="Internal Server Error",
        )
        _, error_count = mgr.pending_count
        assert error_count == 1

    def test_record_parse_error(self):
        mgr = _make_manager()
        mgr.record_parse_error(
            location="device.py:parse_properties",
            exception=ValueError("bad value"),
        )
        _, error_count = mgr.pending_count
        assert error_count == 1

    def test_record_parse_error_with_input_sample(self):
        mgr = _make_manager()
        mgr.record_parse_error(
            location="device.py:parse",
            exception=TypeError("wrong type"),
            input_sample='{"bad": "json"}',
        )
        _, error_count = mgr.pending_count
        assert error_count == 1

    def test_max_pending_errors_limit(self):
        mgr = _make_manager()
        for i in range(MAX_PENDING_ERRORS + 20):
            mgr.record_api_error(
                endpoint=f"/api/endpoint_{i}",
                code=500,
                message=f"Error number {i}",
            )
        _, error_count = mgr.pending_count
        assert error_count <= MAX_PENDING_ERRORS

    def test_duplicate_errors_merged(self):
        mgr = _make_manager()
        mgr.record_api_error(endpoint="/api/x", code=500, message="fail")
        mgr.record_api_error(endpoint="/api/x", code=500, message="fail")
        _, error_count = mgr.pending_count
        # Duplicates are merged (count incremented), not added separately
        assert error_count == 1

    def test_disabled_error_reporting_ignores(self):
        mgr = AnonymousShareManager()
        mgr.set_enabled(True, error_reporting=False, installation_id="test")
        mgr.record_api_error(endpoint="/api/x", code=500, message="fail")
        _, error_count = mgr.pending_count
        assert error_count == 0

    def test_record_unknown_property_and_deduplicate(self):
        mgr = _make_manager()
        mgr.record_unknown_property("light", "foo", "bar")
        mgr.record_unknown_property("light", "foo", "bar")
        _, error_count = mgr.pending_count
        assert error_count == 1

    def test_record_unknown_device_type_and_deduplicate(self):
        mgr = _make_manager()
        mgr.record_unknown_device_type("mystery", 999, "iot-x")
        mgr.record_unknown_device_type("mystery", 999, "iot-x")
        _, error_count = mgr.pending_count
        assert error_count == 1

    def test_record_command_error_creates_error(self):
        mgr = _make_manager()
        mgr.record_command_error(
            command="set",
            device_type="light",
            code=500,
            message="failed",
            params="power=1",
        )
        _, error_count = mgr.pending_count
        assert error_count == 1

    def test_record_unknown_disabled_ignored(self):
        mgr = AnonymousShareManager()
        mgr.set_enabled(True, error_reporting=False, installation_id="test")
        mgr.record_unknown_property("light", "x", 1)
        mgr.record_unknown_device_type("mystery", 1)
        _, error_count = mgr.pending_count
        assert error_count == 0


# ===========================================================================
# TestBuildReport
# ===========================================================================


class TestBuildReport:
    """Tests for build_report output structure."""

    def test_report_structure(self):
        mgr = _make_manager()
        report = mgr.build_report()
        assert "report_version" in report
        assert "integration_version" in report
        assert "generated_at" in report
        assert "installation_id" in report
        assert "device_count" in report
        assert "error_count" in report
        assert "devices" in report
        assert "errors" in report

    def test_report_contains_recorded_devices(self):
        mgr = _make_manager()
        device = _make_mock_device(iot_name="lipro_led", physical_model="light")
        mgr.record_device(device)
        report = mgr.build_report()
        assert report["device_count"] == 1
        assert len(report["devices"]) == 1
        assert report["devices"][0]["iot_name"] == "lipro_led"

    def test_report_contains_recorded_errors(self):
        mgr = _make_manager()
        mgr.record_api_error(endpoint="/api/test", code=404, message="Not Found")
        report = mgr.build_report()
        assert report["error_count"] == 1
        assert len(report["errors"]) == 1
        assert report["errors"][0]["type"] == "api_error"

    def test_report_installation_id(self):
        mgr = _make_manager()
        report = mgr.build_report()
        assert report["installation_id"] == "test-id"

    def test_empty_report(self):
        mgr = _make_manager()
        report = mgr.build_report()
        assert report["device_count"] == 0
        assert report["error_count"] == 0
        assert report["devices"] == []
        assert report["errors"] == []

    def test_get_pending_report_none_when_empty(self):
        mgr = _make_manager()
        assert mgr.get_pending_report() is None


# ===========================================================================
# TestSubmitLogic
# ===========================================================================


class TestSubmitLogic:
    """Tests for submit_if_needed interval and threshold logic."""

    async def test_submit_if_needed_respects_interval(self):
        mgr = _make_manager()
        # Add enough devices to trigger upload threshold
        for i in range(MAX_PENDING_DEVICES):
            d = _make_mock_device(iot_name=f"device_{i}")
            mgr.record_device(d)

        session = MagicMock()
        mock_response = MagicMock()
        mock_response.status = 200

        # Create a proper async context manager for session.post()
        ctx = AsyncMock()
        ctx.__aenter__ = AsyncMock(return_value=mock_response)
        ctx.__aexit__ = AsyncMock(return_value=False)
        session.post = MagicMock(return_value=ctx)

        # Last upload was long ago -> should trigger
        mgr._last_upload_time = 0
        with patch.object(mgr, "_save_reported_devices"):
            result = await mgr.submit_if_needed(session)
        assert result is True

    async def test_submit_if_needed_skips_when_too_soon(self):
        mgr = _make_manager()
        # Add a device but not enough to hit threshold
        device = _make_mock_device(iot_name="lipro_led")
        mgr.record_device(device)

        session = AsyncMock()

        # Last upload was just now, and we don't have enough data
        mgr._last_upload_time = time.time()
        result = await mgr.submit_if_needed(session)
        # Should return True (no submission needed) without calling session
        assert result is True
        session.post.assert_not_called()

    async def test_submit_report_checks_interval(self):
        mgr = _make_manager()
        device = _make_mock_device(iot_name="lipro_led")
        mgr.record_device(device)

        session = AsyncMock()

        # Set last upload to now -> interval not passed
        mgr._last_upload_time = time.time()
        result = await mgr.submit_report(session, force=False)
        # Should skip upload and return True
        assert result is True
        session.post.assert_not_called()

    async def test_submit_disabled_returns_false(self):
        mgr = _make_manager(enabled=False)
        session = AsyncMock()
        result = await mgr.submit_report(session)
        assert result is False

    async def test_submit_empty_returns_true(self):
        mgr = _make_manager()
        session = AsyncMock()
        result = await mgr.submit_report(session)
        # No data to report -> True
        assert result is True

    async def test_submit_report_non_200_returns_false(self):
        mgr = _make_manager()
        mgr.record_device(_make_mock_device(iot_name="lipro_led"))

        session = MagicMock()
        response = MagicMock()
        response.status = 500
        context = AsyncMock()
        context.__aenter__ = AsyncMock(return_value=response)
        context.__aexit__ = AsyncMock(return_value=False)
        session.post = MagicMock(return_value=context)

        assert await mgr.submit_report(session, force=True) is False

    async def test_submit_report_timeout_returns_false(self):
        mgr = _make_manager()
        mgr.record_device(_make_mock_device(iot_name="lipro_led"))

        session = MagicMock()
        session.post = MagicMock(side_effect=TimeoutError)

        assert await mgr.submit_report(session, force=True) is False

    async def test_submit_report_client_error_returns_false(self):
        mgr = _make_manager()
        mgr.record_device(_make_mock_device(iot_name="lipro_led"))

        session = MagicMock()
        session.post = MagicMock(side_effect=aiohttp.ClientError("network down"))

        assert await mgr.submit_report(session, force=True) is False

    @pytest.mark.parametrize("exc", [OSError("disk"), ValueError("bad")])
    async def test_submit_report_unexpected_error_returns_false(self, exc):
        mgr = _make_manager()
        mgr.record_device(_make_mock_device(iot_name="lipro_led"))

        session = MagicMock()
        session.post = MagicMock(side_effect=exc)

        assert await mgr.submit_report(session, force=True) is False

    async def test_submit_if_needed_disabled_returns_true(self):
        mgr = _make_manager(enabled=False)
        session = AsyncMock()
        assert await mgr.submit_if_needed(session) is True
        session.post.assert_not_called()

    async def test_submit_developer_feedback_success(self):
        """Developer feedback submit should not require anonymous-share enabled."""
        mgr = _make_manager(enabled=False)
        mgr._ha_version = "2026.2.0"

        session = MagicMock()
        response = MagicMock()
        response.status = 200
        context = AsyncMock()
        context.__aenter__ = AsyncMock(return_value=response)
        context.__aexit__ = AsyncMock(return_value=False)
        session.post = MagicMock(return_value=context)

        result = await mgr.submit_developer_feedback(
            session,
            {"source": "test", "reports": [{"phone": "13800000000"}]},
        )

        assert result is True
        session.post.assert_called_once()
        payload = session.post.call_args.kwargs["json"]
        assert payload["report_version"] == "1.2"
        assert payload["integration_version"]
        assert payload["devices"] == []
        assert payload["errors"] == []
        assert "developer_feedback" in payload

    async def test_submit_developer_feedback_non_200_returns_false(self):
        mgr = _make_manager(enabled=False)
        session = MagicMock()
        response = MagicMock()
        response.status = 500
        context = AsyncMock()
        context.__aenter__ = AsyncMock(return_value=response)
        context.__aexit__ = AsyncMock(return_value=False)
        session.post = MagicMock(return_value=context)

        result = await mgr.submit_developer_feedback(
            session,
            {"source": "test", "reports": []},
        )
        assert result is False

    def test_build_upload_headers_uses_static_api_key(self):
        headers = ShareWorkerClient.build_upload_headers()
        assert headers["X-API-Key"] == SHARE_API_KEY

    def test_build_upload_headers_includes_bearer_token(self):
        headers = ShareWorkerClient.build_upload_headers(install_token="abc")
        assert headers["Authorization"] == "Bearer abc"

    async def test_submit_report_keeps_install_token_in_memory_only(self, tmp_path):
        mgr = _make_manager()
        mgr._storage_path = str(tmp_path)
        mgr._cache_loaded = True
        mgr.record_device(_make_mock_device(iot_name="lipro_led"))

        session = MagicMock()
        response = MagicMock()
        response.status = 200
        response.headers = {}
        response.json = AsyncMock(
            return_value={
                "success": True,
                "code": "REPORT_ACCEPTED",
                "install_token": "tok-1",
                "token_expires_at": 123,
                "token_refresh_after": 100,
            }
        )
        context = AsyncMock()
        context.__aenter__ = AsyncMock(return_value=response)
        context.__aexit__ = AsyncMock(return_value=False)
        session.post = MagicMock(return_value=context)

        assert await mgr.submit_report(session, force=True) is True
        assert mgr._install_token == "tok-1"
        cache = tmp_path / ".lipro_share_auth.json"
        assert cache.exists() is False


# ===========================================================================
# TestGetAnonymousShareManager
# ===========================================================================


class TestGetAnonymousShareManager:
    """Tests for the singleton accessor."""

    def test_returns_manager_with_hass(self):
        hass = MagicMock()
        hass.data = {}
        mgr = get_anonymous_share_manager(hass)
        assert isinstance(mgr, AnonymousShareManager)

    def test_same_instance_with_same_hass(self):
        hass = MagicMock()
        hass.data = {}
        mgr1 = get_anonymous_share_manager(hass)
        mgr2 = get_anonymous_share_manager(hass)
        assert mgr1 is mgr2

    def test_returns_manager_without_hass(self):
        mgr = get_anonymous_share_manager()
        assert isinstance(mgr, AnonymousShareManager)


# ===========================================================================
# TestSetEnabled
# ===========================================================================


class TestSetEnabled:
    """Tests for set_enabled configuration."""

    def test_enable_sets_flags(self):
        mgr = AnonymousShareManager()
        mgr.set_enabled(True, installation_id="abc")
        assert mgr.is_enabled is True
        assert mgr._installation_id == "abc"

    def test_disable_clears_data(self):
        mgr = _make_manager()
        device = _make_mock_device()
        mgr.record_device(device)
        mgr.record_api_error(endpoint="/x", code=500, message="err")
        assert mgr.pending_count != (0, 0)

        mgr.set_enabled(False)
        assert mgr.is_enabled is False
        assert mgr.pending_count == (0, 0)

    def test_storage_path_defers_cache_load(self, tmp_path):
        mgr = AnonymousShareManager()
        mgr.set_enabled(True, storage_path=str(tmp_path))
        assert mgr._cache_loaded is False


class TestReportedDeviceCache:
    """Tests for reported device cache load/save paths."""

    def test_load_reported_devices_success(self, tmp_path):
        mgr = AnonymousShareManager()
        mgr._storage_path = str(tmp_path)
        cache_file = tmp_path / ".lipro_reported_devices.json"
        cache_file.write_text(
            json.dumps({"devices": ["lipro_led", "lipro_switch"]}),
            encoding="utf-8",
        )

        mgr._load_reported_devices()

        assert mgr._reported_device_keys == {"lipro_led", "lipro_switch"}

    def test_load_reported_devices_invalid_json_logs_warning(self, tmp_path):
        mgr = AnonymousShareManager()
        mgr._storage_path = str(tmp_path)
        cache_file = tmp_path / ".lipro_reported_devices.json"
        cache_file.write_text("{invalid json", encoding="utf-8")

        with patch(
            "custom_components.lipro.core.anonymous_share.manager._LOGGER.warning"
        ) as warn:
            mgr._load_reported_devices()

        warn.assert_called_once()

    def test_save_reported_devices_write_failure_logs_warning(self, tmp_path):
        mgr = AnonymousShareManager()
        mgr._storage_path = str(tmp_path)
        mgr._reported_device_keys = {"lipro_led"}

        with (
            patch("pathlib.Path.write_text", side_effect=OSError("read-only")),
            patch(
                "custom_components.lipro.core.anonymous_share.manager._LOGGER.warning"
            ) as warn,
        ):
            mgr._save_reported_devices()

        warn.assert_called_once()

    async def test_async_ensure_loaded_short_circuit(self):
        mgr = AnonymousShareManager()
        mgr._cache_loaded = True
        with patch("asyncio.to_thread", new=AsyncMock()) as to_thread:
            await mgr.async_ensure_loaded()
        to_thread.assert_not_called()

    async def test_async_ensure_loaded_calls_loader_and_marks_loaded(self):
        mgr = AnonymousShareManager()
        mgr._cache_loaded = False
        with patch("asyncio.to_thread", new=AsyncMock(return_value=None)) as to_thread:
            await mgr.async_ensure_loaded()
        assert to_thread.await_count == 1
        assert mgr._cache_loaded is True

    def test_load_and_save_without_storage_path_noop(self):
        mgr = AnonymousShareManager()
        mgr._storage_path = None
        mgr._load_reported_devices()
        mgr._save_reported_devices()


class TestCapabilities:
    """Tests for capability detection matrix."""

    def test_detect_capabilities_light_order_stable(self):
        """Light capability output order should remain stable."""
        device = _make_mock_device(
            properties={
                PROP_BRIGHTNESS: 1,
                PROP_TEMPERATURE: 5000,
                PROP_FADE_STATE: 1,
                PROP_FOCUS_MODE: 1,
                PROP_SLEEP_AID_ENABLE: 1,
                PROP_WAKE_UP_ENABLE: 1,
            },
            is_light=True,
            has_gear_presets=True,
        )

        assert detect_device_capabilities(device) == [
            "light",
            "brightness",
            "color_temp",
            "gear_presets",
            "fade",
            "focus_mode",
            "sleep_aid",
            "wake_up",
        ]

    def test_detect_capabilities_full_matrix(self):
        device = _make_mock_device(
            properties={
                PROP_BRIGHTNESS: 1,
                PROP_TEMPERATURE: 5000,
                PROP_FADE_STATE: 1,
                PROP_FOCUS_MODE: 1,
                PROP_SLEEP_AID_ENABLE: 1,
                PROP_WAKE_UP_ENABLE: 1,
                PROP_FAN_GEAR: 1,
                PROP_FAN_MODE: 1,
                PROP_POSITION: 1,
                PROP_BATTERY: 99,
                PROP_DOOR_OPEN: 1,
                PROP_BODY_REACTIVE: 1,
                PROP_ACTIVATED: 1,
                PROP_DARK: 1,
                PROP_HEATER_MODE: 1,
                PROP_WIND_GEAR: 1,
                PROP_AERATION_GEAR: 1,
                PROP_LIGHT_MODE: 1,
            },
            is_light=True,
            is_fan_light=True,
            is_curtain=True,
            is_sensor=True,
            is_heater=True,
            is_switch=True,
            is_outlet=True,
            has_gear_presets=True,
        )
        caps = detect_device_capabilities(device)
        expected = {
            "light",
            "brightness",
            "color_temp",
            "gear_presets",
            "fade",
            "focus_mode",
            "sleep_aid",
            "wake_up",
            "fan",
            "fan_speed",
            "fan_mode",
            "cover",
            "position",
            "sensor",
            "battery",
            "door_sensor",
            "motion_sensor",
            "light_sensor",
            "heater",
            "heater_mode",
            "wind_speed",
            "aeration",
            "heater_light",
            "switch",
        }
        assert expected.issubset(set(caps))


class TestScopedAnonymousShareManager:
    """Tests for scoped anonymous-share managers."""

    def test_explicit_entry_scopes_do_not_pollute_each_other(self, monkeypatch):
        monkeypatch.setattr(manager_module, "_share_manager", None)
        hass = MagicMock()
        hass.data = {}

        entry_one_manager = get_anonymous_share_manager(hass, entry_id="entry-1")
        entry_two_manager = get_anonymous_share_manager(hass, entry_id="entry-2")

        entry_one_manager.set_enabled(True, installation_id="install-1")
        entry_two_manager.set_enabled(True, installation_id="install-2")
        entry_one_manager.record_device(_make_mock_device(iot_name="entry_one_light"))
        entry_two_manager.record_api_error(
            endpoint="/api/two", code=500, message="boom"
        )

        assert entry_one_manager._installation_id == "install-1"
        assert entry_two_manager._installation_id == "install-2"
        assert entry_one_manager.pending_count == (1, 0)
        assert entry_two_manager.pending_count == (0, 1)

        aggregate_manager = get_anonymous_share_manager(hass)
        assert aggregate_manager.pending_count == (1, 1)
        report = aggregate_manager.get_pending_report()
        assert report is not None
        assert report["device_count"] == 1
        assert report["error_count"] == 1


class TestObservabilityScope:
    """Tests for observability routing into anonymous-share scopes."""

    def test_default_observability_path_still_records_to_default_scope(
        self, monkeypatch
    ):
        monkeypatch.setattr(manager_module, "_share_manager", None)
        manager = get_anonymous_share_manager()
        manager.set_enabled(True, error_reporting=True, installation_id="default")

        record_observed_api_error("/api/default", 500, "fail", method="POST")

        assert manager.pending_count == (0, 1)
        report = manager.get_pending_report()
        assert report is not None
        assert report["errors"][0]["endpoint"] == "/api/default"

    def test_observability_entry_scope_targets_matching_manager(self, monkeypatch):
        monkeypatch.setattr(manager_module, "_share_manager", None)
        hass = MagicMock()
        hass.data = {}

        entry_one_manager = get_anonymous_share_manager(hass, entry_id="entry-1")
        entry_two_manager = get_anonymous_share_manager(hass, entry_id="entry-2")
        entry_one_manager.set_enabled(True, error_reporting=True, installation_id="one")
        entry_two_manager.set_enabled(True, error_reporting=True, installation_id="two")

        record_observed_api_error(
            "/api/two",
            401,
            "unauthorized",
            method="POST",
            entry_id="entry-2",
        )

        assert entry_one_manager.pending_count == (0, 0)
        assert entry_two_manager.pending_count == (0, 1)


class TestClientObservabilityScope:
    """Tests for explicit entry routing from API client errors."""

    @pytest.mark.asyncio
    async def test_client_records_api_error_with_entry_scope(self, monkeypatch) -> None:
        observed: dict[str, object] = {}

        def _capture(
            endpoint: str,
            code: str | int,
            message: str,
            method: str = "",
            *,
            entry_id: str | None = None,
        ) -> None:
            observed.update(
                {
                    "endpoint": endpoint,
                    "code": code,
                    "message": message,
                    "method": method,
                    "entry_id": entry_id,
                }
            )

        monkeypatch.setattr(
            "custom_components.lipro.core.api.client_auth_recovery._record_api_error",
            _capture,
        )
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000", entry_id="entry-2")

        with pytest.raises(LiproApiError, match="boom"):
            await client._finalize_mapping_result(
                path="/api/test",
                result={"code": 500, "message": "boom"},
                request_token=None,
                is_retry=False,
                retry_on_auth_error=False,
                retry_request=None,
                success_payload=lambda result: result,
            )

        assert observed == {
            "endpoint": "/api/test",
            "code": 500,
            "message": "boom",
            "method": "POST",
            "entry_id": "entry-2",
        }


@pytest.mark.asyncio
async def test_submit_developer_feedback_matches_boundary_fixture() -> None:
    from custom_components.lipro.core.anonymous_share.report_builder import (
        canonicalize_generated_payload,
    )
    from tests.helpers.external_boundary_fixtures import load_external_boundary_fixture

    mgr = AnonymousShareManager()
    mgr.set_enabled(True, error_reporting=True, installation_id="install-001")
    mgr._ha_version = "2026.3.0"
    session = MagicMock()
    submit_share_payload = AsyncMock(return_value=True)
    mgr._share_client = MagicMock(submit_share_payload=submit_share_payload)

    result = await mgr.submit_developer_feedback(session, {"note": "manual run"})

    assert result is True
    assert submit_share_payload.await_args is not None
    report = submit_share_payload.await_args.args[1]
    assert canonicalize_generated_payload(report) == load_external_boundary_fixture(
        "share_worker",
        "developer_feedback_report.canonical.json",
    )
