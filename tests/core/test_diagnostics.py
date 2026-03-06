"""Tests for Lipro diagnostics."""

from __future__ import annotations

from datetime import timedelta
import json
from unittest.mock import MagicMock, patch

import pytest

from custom_components.lipro.const import DOMAIN
from custom_components.lipro.diagnostics import (
    PROPERTY_KEYS_TO_REDACT,
    TO_REDACT,
    _redact_device_properties,
    async_get_config_entry_diagnostics,
    async_get_device_diagnostics,
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

    def test_redact_nested_structures_and_json_string(self):
        """Test recursive redaction for nested dict/list and JSON strings."""
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

        parsed_info = json.loads(result["deviceInfo"])
        assert parsed_info["wifi_ssid"] == "**REDACTED**"
        assert parsed_info["ip"] == "**REDACTED**"
        assert parsed_info["meta"]["iotDeviceId"] == "**REDACTED**"
        assert result["nested"]["gatewayDeviceId"] == "**REDACTED**"
        assert result["nested"]["list"][0]["serial"] == "**REDACTED**"
        assert result["plain"] == "ok"

    def test_redact_literal_identifier_values(self):
        """Test literal MAC/IP/deviceId values are redacted even on non-sensitive keys."""
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
        """Test embedded IP/MAC/deviceId substrings are redacted."""
        props = {
            "note_ip": "peer=10.0.0.8 retry=1",
            "note_mac": "src=AA:BB:CC:DD:EE:FF dst=11:22:33:44:55:66",
            "note_device": "target=03AB5CCD7CABCDEF changed",
            "safe": "hello world",
        }
        result = _redact_device_properties(props)

        assert "10.0.0.8" not in result["note_ip"]
        assert "AA:BB:CC:DD:EE:FF" not in result["note_mac"]
        assert "11:22:33:44:55:66" not in result["note_mac"]
        assert "03AB5CCD7CABCDEF" not in result["note_device"]
        assert "**REDACTED**" in result["note_ip"]
        assert "**REDACTED**" in result["note_mac"]
        assert "**REDACTED**" in result["note_device"]
        assert result["safe"] == "hello world"

    def test_invalid_json_string_fallback_redaction(self):
        """Test malformed JSON strings still go through string redaction path."""
        props = {
            "deviceInfo": "{bad json ip=10.0.0.8 mac=AA:BB:CC:DD:EE:FF}",
        }
        result = _redact_device_properties(props)

        assert "10.0.0.8" not in result["deviceInfo"]
        assert "AA:BB:CC:DD:EE:FF" not in result["deviceInfo"]
        assert result["deviceInfo"].count("**REDACTED**") == 2


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

        assert result["entry"]["title"] == "Lipro (138****0000)"
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

        assert result["entry"]["title"] == "Lipro Empty"
        assert result["devices"] == []
        assert result["coordinator"]["last_update_success"] is False
        assert result["anonymous_share"] == {
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
        coordinator.devices = {device.serial: device}
        coordinator.last_update_success = True
        coordinator.update_interval = timedelta(seconds=30)
        coordinator.mqtt_connected = True

        entry = MagicMock()
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

        assert result["entry"]["title"] == ""
        assert result["devices"][0]["mesh_address"] == 256
        assert result["devices"][0]["is_mesh_gateway"] is True

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
                "power_info": {"nowPower": 0.0, "energyList": []},
                "gateway_device_id": "03ab5ccd7c999999",
            },
            room_name="Master Bedroom",
        )
        coordinator = MagicMock()
        coordinator.devices = {device.serial: device}
        coordinator.last_update_success = True
        coordinator.update_interval = timedelta(seconds=45)
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
                    "extra_data": {
                        "power_info": {"nowPower": 0.0, "energyList": []},
                        "gateway_device_id": "**REDACTED**",
                    },
                },
            ],
        }


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
        coordinator.devices = {device.serial: device}
        coordinator.get_device = MagicMock(return_value=device)
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
        }
        entry.options = {"scan_interval": 30}

        device_entry = MagicMock()
        device_entry.identifiers = {(DOMAIN, device.serial)}

        result = await async_get_device_diagnostics(hass, entry, device_entry)

        assert result["entry"]["title"] == "Lipro (138****0000)"
        assert result["entry"]["data"]["phone"] == "**REDACTED**"
        assert result["device"]["name"] == "**REDACTED**"
        assert result["device"]["room_name"] == "**REDACTED**"
        assert result["device"]["properties"]["mac"] == "**REDACTED**"
        assert result["device"]["properties"]["powerState"] == "1"
        assert result["device"]["extra_data"]["gateway_device_id"] == "**REDACTED**"

    @pytest.mark.asyncio
    async def test_missing_lipro_identifier_returns_error(self, hass):
        """Test diagnostics handles device entries outside lipro domain."""
        coordinator = MagicMock()
        coordinator.devices = {}
        coordinator.get_device = MagicMock(return_value=None)

        entry = MagicMock()
        entry.runtime_data = coordinator
        entry.title = "Lipro (13800000000)"
        entry.data = {}
        entry.options = {}

        device_entry = MagicMock()
        device_entry.identifiers = {("other_domain", "abc")}

        result = await async_get_device_diagnostics(hass, entry, device_entry)
        assert result == {"error": "device_not_in_lipro_domain"}

    @pytest.mark.asyncio
    async def test_unknown_lipro_device_returns_error(self, hass):
        """Test diagnostics handles missing device in coordinator cache."""
        coordinator = MagicMock()
        coordinator.devices = {}
        coordinator.get_device = MagicMock(return_value=None)

        entry = MagicMock()
        entry.runtime_data = coordinator
        entry.title = "Lipro (13800000000)"
        entry.data = {}
        entry.options = {}

        device_entry = MagicMock()
        device_entry.identifiers = {(DOMAIN, "03ab5ccd7c111111")}

        result = await async_get_device_diagnostics(hass, entry, device_entry)
        assert result == {"error": "device_not_found"}
