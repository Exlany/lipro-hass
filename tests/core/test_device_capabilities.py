"""Tests for derived device capability snapshots."""

from __future__ import annotations

from custom_components.lipro.const.categories import DeviceCategory
from custom_components.lipro.core.device import DeviceCapabilities, LiproDevice


def test_device_capabilities_from_device_profile() -> None:
    caps = DeviceCapabilities.from_device_profile(
        device_type_hex="ff000001",
        min_color_temp_kelvin=2700,
        max_color_temp_kelvin=6500,
    )

    assert caps.category == DeviceCategory.LIGHT
    assert caps.is_light is True
    assert caps.is_fan_light is False
    assert caps.supports_color_temp is True


def test_lipro_device_capabilities_property_matches_existing_flags() -> None:
    device = LiproDevice(
        device_number=1,
        serial="03ab5ccd7caaaaaa",
        name="Desk Light",
        device_type=1,
        iot_name="",
        physical_model="light",
    )

    caps = device.capabilities
    assert caps.category == device.category
    assert caps.is_light == device.is_light
    assert caps.is_fan_light == device.is_fan_light
    assert caps.is_curtain == device.is_curtain
    assert caps.is_switch == device.is_switch
    assert caps.is_outlet == device.is_outlet
    assert caps.is_heater == device.is_heater
    assert caps.is_sensor == device.is_sensor
    assert caps.is_body_sensor == device.is_body_sensor
    assert caps.is_door_sensor == device.is_door_sensor
    assert caps.is_gateway == device.is_gateway
    assert caps.supports_color_temp == device.supports_color_temp
