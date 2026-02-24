"""Tests for Lipro diagnostics."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest

from custom_components.lipro.diagnostics import (
    PROPERTY_KEYS_TO_REDACT,
    TO_REDACT,
    _redact_device_properties,
    async_get_config_entry_diagnostics,
)


class TestRedactDeviceProperties:
    """Tests for _redact_device_properties function."""

    def test_redact_mac(self):
        """Test mac is redacted."""
        props = {"mac": "5C:CD:7C:XX:XX:XX", "powerState": "1"}
        result = _redact_device_properties(props)
        assert result["mac"] == "**REDACTED**"
        assert result["powerState"] == "1"

    def test_redact_mac_address(self):
        """Test macAddress is redacted."""
        props = {"macAddress": "5C:CD:7C:XX:XX:XX"}
        result = _redact_device_properties(props)
        assert result["macAddress"] == "**REDACTED**"

    def test_redact_ip(self):
        """Test ip is redacted."""
        props = {"ip": "192.168.1.100"}
        result = _redact_device_properties(props)
        assert result["ip"] == "**REDACTED**"

    def test_redact_ip_address(self):
        """Test ipAddress is redacted."""
        props = {"ipAddress": "192.168.1.100"}
        result = _redact_device_properties(props)
        assert result["ipAddress"] == "**REDACTED**"

    def test_non_sensitive_preserved(self):
        """Test non-sensitive properties are preserved."""
        props = {
            "powerState": "1",
            "brightness": "80",
            "temperature": "4000",
        }
        result = _redact_device_properties(props)
        assert result == props

    def test_redact_wifi_ssid_camel_case(self):
        """Test wifiSsid is redacted."""
        props = {"wifiSsid": "HomeWiFi-5G"}
        result = _redact_device_properties(props)
        assert result["wifiSsid"] == "**REDACTED**"

    def test_empty_properties(self):
        """Test empty properties dict."""
        result = _redact_device_properties({})
        assert result == {}

    def test_case_insensitive_redaction(self):
        """Test redaction is case-insensitive."""
        props = {"MAC": "5C:CD:7C:XX:XX:XX", "IP": "192.168.1.1"}
        result = _redact_device_properties(props)
        assert result["MAC"] == "**REDACTED**"
        assert result["IP"] == "**REDACTED**"


class TestToRedactKeys:
    """Tests for TO_REDACT set completeness."""

    def test_contains_auth_keys(self):
        """Test TO_REDACT contains authentication keys."""
        assert "password" in TO_REDACT
        assert "password_hash" in TO_REDACT
        assert "access_token" in TO_REDACT
        assert "refresh_token" in TO_REDACT
        assert "user_id" in TO_REDACT

    def test_contains_device_id_keys(self):
        """Test TO_REDACT contains device identification keys."""
        assert "serial" in TO_REDACT
        assert "device_id" in TO_REDACT
        assert "deviceId" in TO_REDACT
        assert "groupId" in TO_REDACT
        assert "iotName" in TO_REDACT
        assert "gatewayDeviceId" in TO_REDACT

    def test_contains_user_keys(self):
        """Test TO_REDACT contains user identification keys."""
        assert "phone" in TO_REDACT
        assert "phone_id" in TO_REDACT


class TestPropertyKeysToRedact:
    """Tests for PROPERTY_KEYS_TO_REDACT set completeness."""

    def test_contains_network_keys(self):
        """Test PROPERTY_KEYS_TO_REDACT contains network-related keys."""
        assert "mac" in PROPERTY_KEYS_TO_REDACT
        assert "macAddress" in PROPERTY_KEYS_TO_REDACT
        assert "ip" in PROPERTY_KEYS_TO_REDACT
        assert "ipAddress" in PROPERTY_KEYS_TO_REDACT

    def test_count(self):
        """Test PROPERTY_KEYS_TO_REDACT has expected count."""
        assert len(PROPERTY_KEYS_TO_REDACT) == 7


class TestAsyncGetConfigEntryDiagnostics:
    """Tests for async_get_config_entry_diagnostics."""

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
                "power_info": {"nowPower": 12.5, "energyList": []},
                "gateway_device_id": "03abdeadbeefcafe",
                "ignored": "secret",
            },
            room_name="Bedroom",
        )
        coordinator = MagicMock()
        coordinator.devices = {device.serial: device}
        coordinator.last_update_success = True
        coordinator.update_interval = timedelta(seconds=30)
        coordinator.mqtt_connected = True

        entry = MagicMock()
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
        ):
            result = await async_get_config_entry_diagnostics(hass, entry)

        assert result["entry"]["data"]["phone"] == "**REDACTED**"
        assert result["entry"]["data"]["access_token"] == "**REDACTED**"
        assert result["entry"]["data"]["safe_value"] == "ok"
        assert result["coordinator"]["device_count"] == 1
        assert result["coordinator"]["mqtt_connected"] is True
        assert result["anonymous_share"] == {
            "enabled": True,
            "pending_devices": 2,
            "pending_errors": 1,
        }

        device_info = result["devices"][0]
        assert device_info["name"] == "**REDACTED**"
        assert device_info["room_name"] == "**REDACTED**"
        assert device_info["properties"]["mac"] == "**REDACTED**"
        assert device_info["properties"]["ip"] == "**REDACTED**"
        assert device_info["properties"]["wifi_ssid"] == "**REDACTED**"
        assert device_info["properties"]["powerState"] == "1"
        assert device_info["extra_data"]["power_info"]["nowPower"] == 12.5
        assert device_info["extra_data"]["gateway_device_id"] == "**REDACTED**"
        assert "ignored" not in device_info["extra_data"]

    @pytest.mark.asyncio
    async def test_handles_no_devices(self, hass):
        """Test diagnostics output when coordinator has no devices."""
        coordinator = MagicMock()
        coordinator.devices = {}
        coordinator.last_update_success = False
        coordinator.update_interval = timedelta(seconds=60)
        coordinator.mqtt_connected = False

        entry = MagicMock()
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

        assert result["devices"] == []
        assert result["coordinator"]["last_update_success"] is False
        assert result["anonymous_share"] == {
            "enabled": False,
            "pending_devices": 0,
            "pending_errors": 0,
        }
