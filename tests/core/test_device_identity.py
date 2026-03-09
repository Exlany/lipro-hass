"""Tests for immutable device identity extraction."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from custom_components.lipro.core.device import DeviceIdentity, LiproDevice


def test_device_identity_from_api_data_extracts_expected_fields() -> None:
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
        }
    )

    assert identity.device_number == 123
    assert identity.serial == "03ab5ccd7caaaaaa"
    assert identity.name == "Living Room"
    assert identity.device_type == 6
    assert identity.iot_name == "lipro_led"
    assert identity.room_id == 99
    assert identity.room_name == "Bedroom"
    assert identity.product_id == 888
    assert identity.physical_model == "light"


def test_device_identity_is_frozen() -> None:
    identity = DeviceIdentity.from_api_data({"serial": "03ab5ccd7caaaaaa"})

    with pytest.raises(FrozenInstanceError):
        identity.__setattr__("serial", "mutated")


def test_lipro_device_identity_property_matches_device_fields() -> None:
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
