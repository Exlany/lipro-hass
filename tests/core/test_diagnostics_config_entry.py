"""Tests for config-entry diagnostics surface."""

from __future__ import annotations

from datetime import timedelta
from types import MappingProxyType, SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from custom_components.lipro.control.diagnostics_surface import (
    DiagnosticsPayload,
    DiagnosticsValue,
)
from custom_components.lipro.diagnostics import async_get_config_entry_diagnostics


def _diag_payload(value: DiagnosticsValue) -> DiagnosticsPayload:
    assert isinstance(value, dict)
    return value


def _diag_list(value: DiagnosticsValue) -> list[DiagnosticsValue]:
    assert isinstance(value, list)
    return value


def _diag_str(value: DiagnosticsValue) -> str:
    assert isinstance(value, str)
    return value


class TestAsyncGetConfigEntryDiagnostics:
    """Tests for async_get_config_entry_diagnostics."""

    @pytest.mark.asyncio
    async def test_returns_error_when_entry_not_loaded(self, hass):
        """Test diagnostics returns explicit error if runtime_data is missing."""
        entry = MagicMock()
        entry.runtime_data = None

        result = await async_get_config_entry_diagnostics(hass, entry)

        assert result == {"error": "entry_not_loaded"}

    @pytest.mark.asyncio
    async def test_collects_and_redacts_diagnostics(self, hass, make_device):
        """Test diagnostics payload structure and redaction behavior."""
        device = make_device(
            "outlet",
            name="Office Outlet",
            properties={
                "mac": "5C:CD:7C:AA:BB:CC",
                "ip": "192.168.1.2",
                "wifi_ssid": "HomeWiFi",
                "powerState": "1",
                "version": "1.2.3",
                "wifiRssi": "-58",
                "netType": "wifi",
                "meshAddress": "123",
                "meshType": "1",
                "meshGateway": "1",
            },
            extra_data={
                "gateway_device_id": "03abdeadbeefcafe",
                "ignored": "secret",
            },
            room_name="Bedroom",
        )
        device.outlet_power_info = {"nowPower": 12.5, "energyList": []}

        coordinator = MagicMock()
        coordinator.devices = MappingProxyType({device.serial: device})
        coordinator.last_update_success = True
        coordinator.update_interval = timedelta(seconds=30)
        coordinator.mqtt_service = SimpleNamespace(connected=True)

        entry = MagicMock()
        entry.entry_id = "entry-1"
        entry.runtime_data = coordinator
        entry.title = "Lipro (13800000000)"
        entry.data = {
            "phone": "13800000000",
            "access_token": "token",
            "refresh_token": "refresh",
            "user_id": 10001,
            "safe_value": "ok",
        }
        entry.options = {"debug_mode": False}

        share_manager = MagicMock()
        share_manager.is_enabled = True
        share_manager.pending_count = (2, 1)

        with patch(
            "custom_components.lipro.diagnostics.get_anonymous_share_manager",
            return_value=share_manager,
        ) as get_share_manager:
            result = await async_get_config_entry_diagnostics(hass, entry)

        get_share_manager.assert_called_once_with(hass, entry_id="entry-1")

        entry_view = _diag_payload(result["entry"])
        entry_data = _diag_payload(entry_view["data"])
        coordinator_view = _diag_payload(result["coordinator"])
        anonymous_share_view = _diag_payload(result["anonymous_share"])
        devices = _diag_list(result["devices"])
        device_info = _diag_payload(devices[0])
        device_properties = _diag_payload(device_info["properties"])
        outlet_power_info = _diag_payload(device_info["outlet_power_info"])
        extra_data = _diag_payload(device_info["extra_data"])

        assert entry_view["title"] == "Lipro (138****0000)"
        assert entry_data["phone"] == "**REDACTED**"
        assert entry_data["access_token"] == "**REDACTED**"
        assert entry_data["safe_value"] == "ok"
        assert coordinator_view["device_count"] == 1
        assert coordinator_view["mqtt_connected"] is True
        assert coordinator_view["failure_summary"] == {
            "failure_category": None,
            "failure_origin": None,
            "handling_policy": None,
            "error_type": None,
        }
        assert anonymous_share_view == {
            "enabled": True,
            "pending_devices": 2,
            "pending_errors": 1,
        }

        assert device_info["name"] == "**REDACTED**"
        assert device_info["room_name"] == "**REDACTED**"
        assert device_properties["mac"] == "**REDACTED**"
        assert device_properties["ip"] == "**REDACTED**"
        assert device_properties["wifi_ssid"] == "**REDACTED**"
        assert device_properties["powerState"] == "1"
        assert outlet_power_info["nowPower"] == 12.5
        assert extra_data["gateway_device_id"] == "**REDACTED**"
        assert "ignored" not in extra_data
        assert "power_info" not in extra_data

    @pytest.mark.asyncio
    async def test_projects_normalized_failure_summary_into_coordinator_view(
        self, hass
    ):
        """Diagnostics coordinator view should expose the shared failure summary."""
        coordinator = MagicMock()
        coordinator.devices = MappingProxyType({})
        coordinator.last_update_success = False
        coordinator.update_interval = timedelta(seconds=30)
        coordinator.mqtt_service = SimpleNamespace(connected=False)

        entry = MagicMock()
        entry.entry_id = "entry-1"
        entry.runtime_data = coordinator
        entry.title = "Lipro"
        entry.data = {}
        entry.options = {}

        share_manager = MagicMock()
        share_manager.is_enabled = False
        share_manager.pending_count = (0, 0)
        failure_summary = {
            "failure_category": "network",
            "failure_origin": "protocol.mqtt",
            "handling_policy": "retry",
            "error_type": "TimeoutError",
        }

        with (
            patch(
                "custom_components.lipro.control.diagnostics_surface.build_runtime_diagnostics_projection",
                return_value=MagicMock(
                    snapshot=MagicMock(
                        last_update_success=False,
                        device_count=0,
                        mqtt_connected=False,
                        failure_summary=failure_summary,
                    ),
                    update_interval="0:00:30",
                    degraded_fields=(),
                ),
            ),
            patch(
                "custom_components.lipro.control.diagnostics_surface.build_entry_diagnostics_view",
                return_value={"failure_summary": failure_summary},
            ),
            patch(
                "custom_components.lipro.diagnostics.get_anonymous_share_manager",
                return_value=share_manager,
            ),
        ):
            result = await async_get_config_entry_diagnostics(hass, entry)

        coordinator_view = _diag_payload(result["coordinator"])
        telemetry_view = _diag_payload(result["telemetry"])
        assert coordinator_view["failure_summary"] == failure_summary
        assert telemetry_view["failure_summary"] == failure_summary

    @pytest.mark.asyncio
    async def test_degrades_malformed_runtime_devices_and_share_manager(self, hass):
        """Malformed runtime/share-manager inputs should degrade instead of crashing."""
        coordinator = MagicMock()
        coordinator.devices = object()
        coordinator.last_update_success = False
        coordinator.update_interval = timedelta(seconds=60)
        coordinator.mqtt_service = SimpleNamespace(connected="unknown")

        entry = MagicMock()
        entry.entry_id = "entry-1"
        entry.runtime_data = coordinator
        entry.title = "Lipro Broken"
        entry.data = {"phone": "13800000000"}
        entry.options = {}

        share_manager = MagicMock()
        share_manager.is_enabled = True
        share_manager.pending_count = "broken"

        with patch(
            "custom_components.lipro.diagnostics.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            result = await async_get_config_entry_diagnostics(hass, entry)

        coordinator_view = _diag_payload(result["coordinator"])
        anonymous_share_view = _diag_payload(result["anonymous_share"])
        assert result["devices"] == []
        assert coordinator_view["device_count"] == 0
        assert coordinator_view["mqtt_connected"] is None
        assert coordinator_view["degraded_fields"] == ["devices"]
        assert anonymous_share_view["pending_devices"] == 0
        assert anonymous_share_view["pending_errors"] == 0
        assert anonymous_share_view["degraded"] is True

    async def test_handles_no_devices(self, hass):
        """Test diagnostics output when coordinator has no devices."""
        coordinator = MagicMock()
        coordinator.devices = MappingProxyType({})
        coordinator.last_update_success = False
        coordinator.update_interval = timedelta(seconds=60)
        coordinator.mqtt_service = SimpleNamespace(connected=False)

        entry = MagicMock()
        entry.entry_id = "entry-1"
        entry.runtime_data = coordinator
        entry.title = "Lipro Empty"
        entry.data = {"phone": "13800000000"}
        entry.options = {}

        share_manager = MagicMock()
        share_manager.is_enabled = False
        share_manager.pending_count = (0, 0)

        with patch(
            "custom_components.lipro.diagnostics.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            result = await async_get_config_entry_diagnostics(hass, entry)

        entry_view = _diag_payload(result["entry"])
        coordinator_view = _diag_payload(result["coordinator"])
        anonymous_share_view = _diag_payload(result["anonymous_share"])
        assert entry_view["title"] == "Lipro Empty"
        assert result["devices"] == []
        assert coordinator_view["last_update_success"] is False
        assert anonymous_share_view == {
            "enabled": False,
            "pending_devices": 0,
            "pending_errors": 0,
        }

    @pytest.mark.asyncio
    async def test_non_string_title_and_mesh_fields(self, hass, make_device):
        """Test non-string title redaction and mesh fields in device diagnostics."""
        device = make_device(
            "light",
            properties={
                "address": "256",
                "meshType": "1",
                "gateway": "1",
            },
        )
        coordinator = MagicMock()
        coordinator.devices = MappingProxyType({device.serial: device})
        coordinator.last_update_success = True
        coordinator.update_interval = timedelta(seconds=30)
        coordinator.mqtt_service = SimpleNamespace(connected=True)

        entry = MagicMock()
        entry.entry_id = "entry-1"
        entry.runtime_data = coordinator
        entry.title = 13800000000
        entry.data = {}
        entry.options = {}

        share_manager = MagicMock()
        share_manager.is_enabled = False
        share_manager.pending_count = (0, 0)

        with patch(
            "custom_components.lipro.diagnostics.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            result = await async_get_config_entry_diagnostics(hass, entry)

        entry_view = _diag_payload(result["entry"])
        devices = _diag_list(result["devices"])
        device_view = _diag_payload(devices[0])
        assert entry_view["title"] == ""
        assert device_view["mesh_address"] == 256
        assert device_view["is_mesh_gateway"] is True

    @pytest.mark.asyncio
    async def test_diagnostics_snapshot(
        self,
        hass,
        make_device,
    ) -> None:
        """Test diagnostics payload with snapshot testing."""
        device = make_device(
            "light",
            name="Bedroom Main Light",
            serial="03ab5ccd7c123456",
            properties={
                "powerState": "1",
                "brightness": "76",
                "colorTemp": "4200",
                "mac": "5C:CD:7C:AA:BB:CC",
                "ipAddress": "192.168.1.8",
            },
            extra_data={
                "gateway_device_id": "03ab5ccd7c999999",
            },
            room_name="Master Bedroom",
        )
        device.outlet_power_info = {"nowPower": 0.0, "energyList": []}

        coordinator = MagicMock()
        coordinator.devices = MappingProxyType({device.serial: device})
        coordinator.last_update_success = True
        coordinator.update_interval = timedelta(seconds=45)
        coordinator.mqtt_service = SimpleNamespace(connected=True)

        entry = MagicMock()
        entry.entry_id = "entry-1"
        entry.runtime_data = coordinator
        entry.title = "Lipro (13800000000)"
        entry.data = {
            "phone": "13800000000",
            "access_token": "token",
            "refresh_token": "refresh",
            "user_id": 10001,
            "safe_value": "ok",
        }
        entry.options = {
            "scan_interval": 45,
            "anonymous_share_enabled": True,
        }

        share_manager = MagicMock()
        share_manager.is_enabled = True
        share_manager.pending_count = (1, 0)

        with patch(
            "custom_components.lipro.diagnostics.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            result = await async_get_config_entry_diagnostics(hass, entry)

        assert result == {
            "entry": {
                "title": "Lipro (138****0000)",
                "data": {
                    "phone": "**REDACTED**",
                    "access_token": "**REDACTED**",
                    "refresh_token": "**REDACTED**",
                    "user_id": "**REDACTED**",
                    "safe_value": "ok",
                },
                "options": {
                    "scan_interval": 45,
                    "anonymous_share_enabled": True,
                },
            },
            "coordinator": {
                "last_update_success": True,
                "update_interval": "0:00:45",
                "mqtt_connected": True,
                "device_count": 1,
                "failure_summary": {
                    "failure_category": None,
                    "failure_origin": None,
                    "handling_policy": None,
                    "error_type": None,
                },
            },
            "anonymous_share": {
                "enabled": True,
                "pending_devices": 1,
                "pending_errors": 0,
            },
            "devices": [
                {
                    "name": "**REDACTED**",
                    "available": True,
                    "is_connected": True,
                    "category": 1,
                    "device_type": 1,
                    "device_type_hex": "ff000001",
                    "physical_model": "light",
                    "is_group": False,
                    "room_name": "**REDACTED**",
                    "properties": {
                        "powerState": "1",
                        "brightness": "76",
                        "colorTemp": "4200",
                        "mac": "**REDACTED**",
                        "ipAddress": "**REDACTED**",
                    },
                    "outlet_power_info": {"nowPower": 0.0, "energyList": []},
                    "extra_data": {
                        "gateway_device_id": "**REDACTED**",
                    },
                },
            ],
        }
