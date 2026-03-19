"""Tests for AnonymousShareManager."""

from __future__ import annotations

import json
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.lipro.core.anonymous_share import manager as manager_module
from custom_components.lipro.core.anonymous_share.const import MAX_PENDING_ERRORS
from custom_components.lipro.core.anonymous_share.manager import (
    AnonymousShareManager,
    get_anonymous_share_manager,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
from .support import _make_manager, _make_mock_device


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
        devices = cast(list[dict[str, object]], report["devices"])
        assert report["device_count"] == 1
        assert len(devices) == 1
        assert devices[0]["iot_name"] == "lipro_led"

    def test_report_contains_recorded_errors(self):
        mgr = _make_manager()
        mgr.record_api_error(endpoint="/api/test", code=404, message="Not Found")
        report = mgr.build_report()
        errors = cast(list[dict[str, object]], report["errors"])
        assert report["error_count"] == 1
        assert len(errors) == 1
        assert errors[0]["type"] == "api_error"

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

class TestScopedAnonymousShareManager:
    """Tests for scoped anonymous-share managers."""

    def test_explicit_entry_scopes_do_not_pollute_each_other(self, monkeypatch):
        manager_module._get_root_manager.cache_clear()
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
