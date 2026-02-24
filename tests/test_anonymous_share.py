"""Tests for AnonymousShareManager."""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro.core.anonymous_share import (
    MAX_PENDING_DEVICES,
    MAX_PENDING_ERRORS,
    MIN_UPLOAD_INTERVAL,
    REDACT_KEYS,
    AnonymousShareManager,
    SharedDevice,
    SharedError,
    _MAX_STRING_LENGTH,
    get_anonymous_share_manager,
)


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
    properties: dict | None = None,
    firmware_version: str | None = "1.0.0",
    min_color_temp_kelvin: int = 2700,
    max_color_temp_kelvin: int = 6500,
    gear_list: list | None = None,
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
    device.category = MagicMock()
    device.category.value = "light"
    return device


# ===========================================================================
# TestLooksSensitive
# ===========================================================================


class TestLooksSensitive:
    """Tests for _looks_sensitive detection."""

    def setup_method(self):
        self.mgr = _make_manager(enabled=False)

    def test_mac_address_detected(self):
        assert self.mgr._looks_sensitive("5C:CD:7C:AA:BB:CC") is True

    def test_mac_address_with_dashes_detected(self):
        assert self.mgr._looks_sensitive("5C-CD-7C-AA-BB-CC") is True

    def test_ip_address_detected(self):
        assert self.mgr._looks_sensitive("192.168.1.100") is True

    def test_device_id_detected(self):
        assert self.mgr._looks_sensitive("03ab5ccd7c123456") is True

    def test_token_like_detected(self):
        token = "a" * 32
        assert self.mgr._looks_sensitive(token) is True

    def test_long_mixed_token_detected(self):
        token = "abcDEF012345_-abcDEF012345_-abcDEF"
        assert self.mgr._looks_sensitive(token) is True

    def test_normal_value_not_sensitive(self):
        assert self.mgr._looks_sensitive("hello") is False
        assert self.mgr._looks_sensitive("100") is False
        assert self.mgr._looks_sensitive("powerState") is False

    def test_short_string_not_sensitive(self):
        assert self.mgr._looks_sensitive("1") is False
        assert self.mgr._looks_sensitive("on") is False


# ===========================================================================
# TestSanitizeString
# ===========================================================================


class TestSanitizeString:
    """Tests for _sanitize_string replacement logic."""

    def setup_method(self):
        self.mgr = _make_manager(enabled=False)

    def test_replaces_mac_addresses(self):
        result = self.mgr._sanitize_string("device mac is 5C:CD:7C:AA:BB:CC here")
        assert "[MAC]" in result
        assert "5C:CD:7C:AA:BB:CC" not in result

    def test_replaces_ip_addresses(self):
        result = self.mgr._sanitize_string("host at 192.168.1.100 responded")
        assert "[IP]" in result
        assert "192.168.1.100" not in result

    def test_replaces_device_ids(self):
        result = self.mgr._sanitize_string("device 03ab5ccd7c123456 offline")
        assert "[DEVICE_ID]" in result
        assert "03ab5ccd7c123456" not in result

    def test_preserves_normal_text(self):
        text = "powerState changed to on"
        assert self.mgr._sanitize_string(text) == text

    def test_truncates_long_strings(self):
        """_sanitize_string itself does not truncate; _sanitize_value does."""
        # Use a string with spaces so it doesn't match _RE_TOKEN_LIKE
        long_str = "hello world " * ((_MAX_STRING_LENGTH // 12) + 50)
        assert len(long_str) > _MAX_STRING_LENGTH

        # _sanitize_string only does regex replacement, not truncation
        result = self.mgr._sanitize_string(long_str)
        assert len(result) == len(long_str)

        # _sanitize_value truncates long strings
        result_val = self.mgr._sanitize_value(long_str)
        assert "...[truncated]" in result_val
        assert len(result_val) < len(long_str)


# ===========================================================================
# TestSanitizeProperties
# ===========================================================================


class TestSanitizeProperties:
    """Tests for _sanitize_properties dict sanitization."""

    def setup_method(self):
        self.mgr = _make_manager(enabled=False)

    def test_redacts_known_keys(self):
        props = {
            "deviceId": "secret-id",
            "mac": "5C:CD:7C:AA:BB:CC",
            "serial": "some-serial",
            "powerState": "1",
        }
        result = self.mgr._sanitize_properties(props)
        # Known sensitive keys are completely removed (not present)
        assert "deviceId" not in result
        assert "mac" not in result
        assert "serial" not in result
        # Safe keys are preserved
        assert "powerState" in result
        assert result["powerState"] == "1"

    def test_preserves_safe_properties(self):
        props = {
            "powerState": "1",
            "brightness": 80,
            "temperature": 4000,
        }
        result = self.mgr._sanitize_properties(props)
        assert result["powerState"] == "1"
        assert result["brightness"] == 80
        assert result["temperature"] == 4000

    def test_sanitizes_values_with_embedded_sensitive_data(self):
        props = {
            "info": "5C:CD:7C:AA:BB:CC",  # MAC as a value
        }
        result = self.mgr._sanitize_properties(props)
        # The value looks sensitive (exact MAC match), so it gets redacted
        assert result["info"] == "[redacted]"

    def test_redact_keys_case_insensitive(self):
        props = {"DEVICEID": "secret", "Mac": "aa:bb:cc:dd:ee:ff"}
        result = self.mgr._sanitize_properties(props)
        assert "DEVICEID" not in result
        assert "Mac" not in result


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

    def test_storage_path_defers_cache_load(self):
        mgr = AnonymousShareManager()
        mgr.set_enabled(True, storage_path="/tmp/test")
        assert mgr._cache_loaded is False