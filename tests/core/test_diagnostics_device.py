"""Tests for device diagnostics surface."""

from __future__ import annotations

from datetime import timedelta
from types import MappingProxyType, SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.control.diagnostics_surface import (
    DiagnosticsPayload,
    DiagnosticsValue,
)
from custom_components.lipro.diagnostics import async_get_device_diagnostics


def _diag_payload(value: DiagnosticsValue) -> DiagnosticsPayload:
    assert isinstance(value, dict)
    return value


def _diag_list(value: DiagnosticsValue) -> list[DiagnosticsValue]:
    assert isinstance(value, list)
    return value


def _diag_str(value: DiagnosticsValue) -> str:
    assert isinstance(value, str)
    return value


class TestAsyncGetDeviceDiagnostics:
    """Tests for async_get_device_diagnostics."""

    @pytest.mark.asyncio
    async def test_returns_error_when_entry_not_loaded(self, hass):
        """Test device diagnostics returns explicit error if runtime_data is missing."""
        entry = MagicMock()
        entry.runtime_data = None

        device_entry = MagicMock()
        device_entry.identifiers = {(DOMAIN, "03ab5ccd7c111111")}

        result = await async_get_device_diagnostics(hass, entry, device_entry)

        assert result == {"error": "entry_not_loaded"}

    @pytest.mark.asyncio
    async def test_collects_single_device_diagnostics(self, hass, make_device):
        """Test device diagnostics returns redacted payload for one device."""
        device = make_device(
            "light",
            serial="03ab5ccd7c654321",
            properties={
                "powerState": "1",
                "mac": "5C:CD:7C:AA:BB:CC",
            },
            extra_data={"gateway_device_id": "03ab5ccd7c999999"},
            room_name="Bedroom",
        )

        coordinator = MagicMock()
        coordinator.devices = MappingProxyType({device.serial: device})
        coordinator.get_device = MagicMock(return_value=device)
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
        }
        entry.options = {"scan_interval": 30}

        device_entry = MagicMock()
        device_entry.identifiers = {(DOMAIN, device.serial)}

        result = await async_get_device_diagnostics(hass, entry, device_entry)

        entry_view = _diag_payload(result["entry"])
        entry_data = _diag_payload(entry_view["data"])
        device_view = _diag_payload(result["device"])
        properties = _diag_payload(device_view["properties"])
        extra_data = _diag_payload(device_view["extra_data"])

        assert entry_view["title"] == "Lipro (138****0000)"
        assert entry_data["phone"] == "**REDACTED**"
        assert device_view["name"] == "**REDACTED**"
        assert device_view["room_name"] == "**REDACTED**"
        assert properties["mac"] == "**REDACTED**"
        assert properties["powerState"] == "1"
        assert extra_data["gateway_device_id"] == "**REDACTED**"

    @pytest.mark.asyncio
    async def test_missing_lipro_identifier_returns_error(self, hass):
        """Test diagnostics handles device entries outside lipro domain."""
        coordinator = MagicMock()
        coordinator.devices = MappingProxyType({})
        coordinator.get_device = MagicMock(return_value=None)

        entry = MagicMock()
        entry.entry_id = "entry-1"
        entry.runtime_data = coordinator
        entry.title = "Lipro (13800000000)"
        entry.data = {}
        entry.options = {}

        device_entry = MagicMock()
        device_entry.identifiers = {("other_domain", "abc")}

        result = await async_get_device_diagnostics(hass, entry, device_entry)
        assert result == {"error": "device_not_in_lipro_domain"}

    @pytest.mark.asyncio
    async def test_device_diagnostics_reports_unavailable_cache_for_malformed_runtime(
        self, hass
    ):
        coordinator = MagicMock()
        coordinator.devices = object()
        coordinator.get_device = None

        entry = MagicMock()
        entry.entry_id = "entry-1"
        entry.runtime_data = coordinator
        entry.title = "Lipro (13800000000)"
        entry.data = {}
        entry.options = {}

        device_entry = MagicMock()
        device_entry.identifiers = {(DOMAIN, "03ab5ccd7c111111")}

        result = await async_get_device_diagnostics(hass, entry, device_entry)

        assert result == {"error": "device_cache_unavailable"}

    @pytest.mark.asyncio
    async def test_unknown_lipro_device_returns_error(self, hass):
        """Test diagnostics handles missing device in coordinator cache."""
        coordinator = MagicMock()
        coordinator.devices = MappingProxyType({})
        coordinator.get_device = MagicMock(return_value=None)

        entry = MagicMock()
        entry.entry_id = "entry-1"
        entry.runtime_data = coordinator
        entry.title = "Lipro (13800000000)"
        entry.data = {}
        entry.options = {}

        device_entry = MagicMock()
        device_entry.identifiers = {(DOMAIN, "03ab5ccd7c111111")}

        result = await async_get_device_diagnostics(hass, entry, device_entry)
        assert result == {"error": "device_not_found"}

    @pytest.mark.asyncio
    async def test_device_diagnostics_delegates_device_lookup_to_runtime_access(self, hass, make_device):
        """Device diagnostics should reuse runtime_access lookup helpers."""
        device = make_device("light", properties={"powerState": "1"})
        coordinator = MagicMock()
        coordinator.devices = MappingProxyType({})

        entry = MagicMock()
        entry.entry_id = "entry-1"
        entry.runtime_data = coordinator
        entry.title = "Lipro (13800000000)"
        entry.data = {}
        entry.options = {}

        device_entry = MagicMock()
        device_entry.identifiers = {(DOMAIN, "03ab5ccd7c111111")}

        with patch(
            "custom_components.lipro.control.diagnostics_surface.find_runtime_device_for_entry",
            return_value=device,
        ) as runtime_lookup:
            result = await async_get_device_diagnostics(hass, entry, device_entry)

        runtime_lookup.assert_called_once_with(entry, "03ab5ccd7c111111")
        assert result["device"]
