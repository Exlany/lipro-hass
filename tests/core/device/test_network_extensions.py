"""Tests for Lipro device model."""

from __future__ import annotations

from custom_components.lipro.core.device import LiproDevice


class TestDeviceNetworkProperties:
    """Tests for network/diagnostic properties."""

    def test_ip_address(self):
        """Test IP address property."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={"ip": "192.168.1.100"},
        )
        assert device.ip_address == "192.168.1.100"

    def test_ip_address_missing(self):
        """Test IP address returns None when missing."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
        )
        assert device.ip_address is None

    def test_wifi_ssid(self):
        """Test WiFi SSID property."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={"wifi_ssid": "MyNetwork"},
        )
        assert device.wifi_ssid == "MyNetwork"

    def test_wifi_rssi(self):
        """Test WiFi RSSI property."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={"wifi_rssi": "-55"},
        )
        assert device.wifi_rssi == -55

    def test_wifi_rssi_missing(self):
        """Test WiFi RSSI returns None when missing."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
        )
        assert device.wifi_rssi is None

    def test_mac_address(self):
        """Test MAC address property."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={"mac": "AA:BB:CC:DD:EE:FF"},
        )
        assert device.mac_address == "AA:BB:CC:DD:EE:FF"

    def test_firmware_version(self):
        """Test firmware version property."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={"version": "1.2.3"},
        )
        assert device.firmware_version == "1.2.3"

    def test_net_type(self):
        """Test network type property."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={"net_type": "wifi"},
        )
        assert device.net_type == "wifi"


class TestDeviceMeshProperties:
    """Tests for Mesh network properties."""

    def test_mesh_address(self):
        """Test Mesh address property."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={"address": "256"},
        )
        assert device.mesh_address == 256

    def test_mesh_address_missing(self):
        """Test Mesh address returns None when missing."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
        )
        assert device.mesh_address is None

    def test_mesh_type(self):
        """Test Mesh type property."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={"meshType": "1"},
        )
        assert device.mesh_type == 1

    def test_is_mesh_gateway(self):
        """Test Mesh gateway detection."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Gateway",
            device_type=1,
            iot_name="",
            properties={"gateway": "1"},
        )
        assert device.is_mesh_gateway is True

    def test_ble_mac(self):
        """Test BLE MAC address property."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={"bleMac": "5C:CD:7C:XX:XX:XX"},
        )
        assert device.ble_mac == "5C:CD:7C:XX:XX:XX"

    def test_latest_sync_timestamp(self):
        """Test latest sync timestamp property."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={"latestSyncTimestamp": "1700000000000"},
        )
        assert device.latest_sync_timestamp == 1700000000000

    def test_latest_sync_timestamp_missing(self):
        """Test latest sync timestamp returns None when missing."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
        )
        assert device.latest_sync_timestamp is None

    def test_rc_list_parses_gateway_remote_list(self):
        """Test rcList JSON is decoded into a structured list."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Gateway",
            device_type=11,
            iot_name="M2W1",
            physical_model="gateway",
            properties={
                "rcList": '[{"address":"5ccd7c59abcd","keycount":1,"keyindex":1,"name":"智能控制器","selfIndex":-1,"timestamp":"1683097773619","version":"3.1.0"}]'
            },
        )

        assert device.rc_list == [
            {
                "address": "5ccd7c59abcd",
                "keycount": 1,
                "keyindex": 1,
                "name": "智能控制器",
                "selfIndex": -1,
                "timestamp": "1683097773619",
                "version": "3.1.0",
            }
        ]

    def test_ir_remote_helpers(self):
        """Test IR remote helper getters use encoded device id safely."""
        device = LiproDevice(
            device_number=1,
            serial="rmt_id_appremote_realremote_03ab5ccd7c123456",
            name="IR Remote",
            device_type=11,
            iot_name="irRemote",
            physical_model="irRemote",
            properties={"irSwitch": "0"},
        )

        assert device.is_ir_remote_device is True
        assert device.ir_remote_gateway_device_id == "03ab5ccd7c123456"
        assert device.supports_ir_switch is True
        assert device.ir_switch_enabled is False

    def test_ir_remote_device_driver_id_has_no_parent_gateway(self):
        """Test driver-owned IR remotes do not invent a parent gateway id."""
        device = LiproDevice(
            device_number=1,
            serial="rmt_id_appremote_realremote_00000000",
            name="IR Driver Remote",
            device_type=11,
            iot_name="irRemote",
            physical_model="irRemote",
        )

        assert device.ir_remote_gateway_device_id is None
