"""Tests for structured device network info extraction."""

from __future__ import annotations

from custom_components.lipro.core.device import DeviceNetworkInfo, LiproDevice


def test_device_network_info_from_properties_extracts_expected_fields() -> None:
    info = DeviceNetworkInfo.from_properties(
        {
            "ip": "192.168.1.88",
            "wifi_ssid": "Home WiFi",
            "wifi_rssi": "-65",
            "net_type": "wifi",
            "mac": "AA:BB:CC:DD:EE:FF",
            "version": "1.0.3",
            "latestSyncTimestamp": 123456,
            "address": "7",
            "meshType": 1,
            "gateway": "1",
            "bleMac": "11:22:33:44:55:66",
        }
    )

    assert info.ip_address == "192.168.1.88"
    assert info.wifi_ssid == "Home WiFi"
    assert info.wifi_rssi == -65
    assert info.net_type == "wifi"
    assert info.mac_address == "AA:BB:CC:DD:EE:FF"
    assert info.firmware_version == "1.0.3"
    assert info.latest_sync_timestamp == 123456
    assert info.mesh_address == 7
    assert info.mesh_type == 1
    assert info.is_mesh_gateway is True
    assert info.ble_mac == "11:22:33:44:55:66"


def test_lipro_device_network_info_property_matches_existing_accessors() -> None:
    device = LiproDevice(
        device_number=1,
        serial="03ab5ccd7caaaaaa",
        name="Gateway",
        device_type=1,
        iot_name="gateway",
        properties={
            "ip": "192.168.1.88",
            "wifi_ssid": "Home WiFi",
            "wifi_rssi": -60,
            "net_type": "wifi",
            "mac": "AA:BB:CC:DD:EE:FF",
            "version": "1.0.3",
            "latestSyncTimestamp": 123456,
            "address": 7,
            "meshType": 1,
            "gateway": True,
            "bleMac": "11:22:33:44:55:66",
        },
    )

    info = device.network_info
    assert info.ip_address == device.ip_address
    assert info.wifi_ssid == device.wifi_ssid
    assert info.wifi_rssi == device.wifi_rssi
    assert info.net_type == device.net_type
    assert info.mac_address == device.mac_address
    assert info.firmware_version == device.firmware_version
    assert info.latest_sync_timestamp == device.latest_sync_timestamp
    assert info.mesh_address == device.mesh_address
    assert info.mesh_type == device.mesh_type
    assert info.is_mesh_gateway == device.is_mesh_gateway
    assert info.ble_mac == device.ble_mac
