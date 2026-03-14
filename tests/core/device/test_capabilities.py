"""Tests for device capability snapshots under the modularized layout."""

from __future__ import annotations

import pytest

from custom_components.lipro.const.categories import DeviceCategory
from custom_components.lipro.core.capability import (
    CapabilityRegistry,
    CapabilitySnapshot,
)


def test_device_capabilities_from_device_profile_exposes_light_flags() -> None:
    """Profile metadata should derive the expected light capability set."""
    caps = CapabilityRegistry.from_device_profile(
        device_type_hex="ff000001",
        min_color_temp_kelvin=2700,
        max_color_temp_kelvin=6500,
        max_fan_gear=6,
    )

    assert isinstance(caps, CapabilitySnapshot)
    assert caps.category == DeviceCategory.LIGHT
    assert caps.platforms == ("light",)
    assert caps.is_light is True
    assert caps.is_fan_light is False
    assert caps.supports_color_temp is True
    assert caps.max_fan_gear == 6


@pytest.mark.parametrize(
    ("device_type_hex", "expected_category", "expected_platforms", "attr_name"),
    [
        ("ff000006", DeviceCategory.OUTLET, ("switch",), "is_outlet"),
        ("ff000003", DeviceCategory.SWITCH, ("switch",), "is_switch"),
        (
            "ff000008",
            DeviceCategory.BODY_SENSOR,
            ("binary_sensor",),
            "is_body_sensor",
        ),
        (
            "ff00000a",
            DeviceCategory.DOOR_SENSOR,
            ("binary_sensor",),
            "is_door_sensor",
        ),
        ("ff00000b", DeviceCategory.GATEWAY, (), "is_gateway"),
    ],
)
def test_device_capabilities_from_device_type_maps_categories(
    device_type_hex: str,
    expected_category: DeviceCategory,
    expected_platforms: tuple[str, ...],
    attr_name: str,
) -> None:
    """Type-only capability snapshots should still expose category flags."""
    caps = CapabilityRegistry.from_device_type(device_type_hex)

    assert caps.category == expected_category
    assert caps.platforms == expected_platforms
    assert getattr(caps, attr_name) is True
    assert caps.supports_color_temp is False


def test_lipro_device_capabilities_property_matches_facade_flags(
    make_device,
) -> None:
    """Facade capability delegation should stay aligned with helper snapshots."""
    device = make_device("light", serial="03ab5ccd7caaaaaa", name="Desk Light")

    caps = device.capabilities
    assert isinstance(caps, CapabilitySnapshot)
    assert caps.category == device.category
    assert caps.platforms == tuple(device.platforms)
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
