"""Tests for immutable device identity snapshots."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from custom_components.lipro.core.device import DeviceIdentity, LiproDevice


def test_device_identity_from_api_data_extracts_supported_fields() -> None:
    """Identity parser should coerce the full supported payload shape."""
    identity = DeviceIdentity.from_api_data(
        {
            "deviceId": "123",
            "serial": "03ab5ccd7caaaaaa",
            "deviceName": "Living Room",
            "type": 6,
            "iotName": "lipro_led",
            "roomId": "99",
            "roomName": "Bedroom",
            "productId": 888,
            "physicalModel": "light",
            "mac": "AA:BB:CC:DD:EE:FF",
            "model": "Lipro X1",
            "firmwareVersion": "1.0.8",
        }
    )

    assert identity == DeviceIdentity(
        device_number=123,
        serial="03ab5ccd7caaaaaa",
        name="Living Room",
        device_type=6,
        iot_name="lipro_led",
        room_id=99,
        room_name="Bedroom",
        product_id=888,
        physical_model="light",
        mac="AA:BB:CC:DD:EE:FF",
        model="Lipro X1",
        firmware="1.0.8",
    )
    assert identity.device_id == 123
    assert identity.device_name == "Living Room"


def test_device_identity_uses_safe_defaults_and_version_fallback() -> None:
    """Identity parser should safely default invalid values."""
    identity = DeviceIdentity.from_api_data(
        {
            "deviceId": object(),
            "deviceName": None,
            "type": True,
            "roomId": "invalid",
            "firmwareVersion": None,
            "version": "2.1.0",
        }
    )

    assert identity.device_number == 0
    assert identity.serial == ""
    assert identity.name == "Unknown"
    assert identity.device_type == 1
    assert identity.room_id == 0
    assert identity.firmware == "2.1.0"


def test_device_identity_is_frozen() -> None:
    """Identity snapshots should stay immutable."""
    identity = DeviceIdentity.from_api_data({"serial": "03ab5ccd7caaaaaa"})

    with pytest.raises(FrozenInstanceError):
        identity.__setattr__("serial", "mutated")


def test_lipro_device_identity_property_matches_facade_fields() -> None:
    """Facade identity view should mirror the device dataclass fields."""
    device = LiproDevice.from_api_data(
        {
            "deviceId": 123,
            "serial": "03ab5ccd7caaaaaa",
            "deviceName": "Desk Light",
            "type": 6,
            "iotName": "lipro_led",
            "roomId": 7,
            "roomName": "Office",
            "productId": 99,
            "physicalModel": "light",
        }
    )

    assert device.identity == DeviceIdentity(
        device_number=123,
        serial="03ab5ccd7caaaaaa",
        name="Desk Light",
        device_type=6,
        iot_name="lipro_led",
        room_id=7,
        room_name="Office",
        product_id=99,
        physical_model="light",
    )
