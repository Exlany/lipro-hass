"""Snapshot coverage for representative device payloads."""

from __future__ import annotations

from syrupy.assertion import SnapshotAssertion

from custom_components.lipro.core.device import LiproDevice


def _device_snapshot(device: LiproDevice) -> dict[str, object]:
    return {
        "identity": {
            "device_number": device.identity.device_number,
            "serial": device.identity.serial,
            "name": device.identity.name,
            "room_name": device.identity.room_name,
        },
        "category": device.category.value,
        "platforms": device.platforms,
        "state": {
            "is_on": device.is_on,
            "brightness": device.brightness,
            "color_temp": device.color_temp,
            "is_connected": device.is_connected,
        },
        "network": {
            "ip_address": device.ip_address,
            "wifi_rssi": device.wifi_rssi,
            "connection_quality": device.connection_quality,
        },
    }


def test_light_device_snapshot(snapshot: SnapshotAssertion) -> None:
    device = LiproDevice(
        device_number=1,
        serial="03ab5ccd7caaaaaa",
        name="Desk Light",
        device_type=1,
        iot_name="lipro_led",
        room_name="Office",
        physical_model="light",
        properties={
            "powerState": "1",
            "brightness": "66",
            "temperature": "50",
            "connectState": "1",
            "ip": "192.168.1.88",
            "wifiRssi": "-65",
        },
    )

    assert _device_snapshot(device) == snapshot
