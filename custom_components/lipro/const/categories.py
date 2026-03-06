"""Device category enumeration for Lipro integration.

This module provides a clean way to categorize devices by their function,
independent of the raw device type codes from the API.
"""

from __future__ import annotations

from enum import Enum, auto
from functools import cache

__all__ = [
    "CATEGORY_TO_PLATFORMS",
    "DeviceCategory",
    "get_device_category",
    "get_platforms_for_category",
    "is_light_category",
    "is_sensor_category",
    "is_switch_category",
]


class DeviceCategory(Enum):
    """Device category enumeration.

    This provides a cleaner way to categorize devices than using raw type codes.
    """

    LIGHT = auto()  # Regular lights (LED, ceiling lamp, desk lamp)
    FAN_LIGHT = auto()  # Fan with integrated light
    CURTAIN = auto()  # Curtains and blinds
    SWITCH = auto()  # Switch panels
    OUTLET = auto()  # Power outlets
    HEATER = auto()  # Heaters (bathroom heaters, etc.)
    BODY_SENSOR = auto()  # Motion/body sensors
    DOOR_SENSOR = auto()  # Door/window sensors
    GATEWAY = auto()  # Mesh gateway devices
    UNKNOWN = auto()  # Unknown device type


@cache
def _get_device_category_map() -> dict[str, DeviceCategory]:
    """Build and cache the device type to category mapping.

    Uses functools.cache for thread-safe lazy initialization.
    """
    from .device_types import (  # noqa: PLC0415
        DEVICE_TYPE_CEILING_LAMP,
        DEVICE_TYPE_CURTAIN,
        DEVICE_TYPE_DESK_LAMP,
        DEVICE_TYPE_FAN_LIGHT,
        DEVICE_TYPE_GATEWAY,
        DEVICE_TYPE_HEATER,
        DEVICE_TYPE_LED,
        DEVICE_TYPE_OUTLET,
        DEVICE_TYPE_PANEL,
        DEVICE_TYPE_SENSOR_D1,
        DEVICE_TYPE_SENSOR_M1,
    )

    return {
        DEVICE_TYPE_LED: DeviceCategory.LIGHT,
        DEVICE_TYPE_CEILING_LAMP: DeviceCategory.LIGHT,
        DEVICE_TYPE_DESK_LAMP: DeviceCategory.LIGHT,
        DEVICE_TYPE_FAN_LIGHT: DeviceCategory.FAN_LIGHT,
        DEVICE_TYPE_CURTAIN: DeviceCategory.CURTAIN,
        DEVICE_TYPE_PANEL: DeviceCategory.SWITCH,
        DEVICE_TYPE_OUTLET: DeviceCategory.OUTLET,
        DEVICE_TYPE_HEATER: DeviceCategory.HEATER,
        DEVICE_TYPE_SENSOR_M1: DeviceCategory.BODY_SENSOR,
        DEVICE_TYPE_SENSOR_D1: DeviceCategory.DOOR_SENSOR,
        DEVICE_TYPE_GATEWAY: DeviceCategory.GATEWAY,
    }


def get_device_category(device_type_hex: str) -> DeviceCategory:
    """Get the device category for a given device type hex code.

    Args:
        device_type_hex: Device type as hex string (e.g., "ff000001").

    Returns:
        DeviceCategory for the device type.

    """
    return _get_device_category_map().get(device_type_hex, DeviceCategory.UNKNOWN)


def is_light_category(category: DeviceCategory) -> bool:
    """Check if category is any type of light."""
    return category in (DeviceCategory.LIGHT, DeviceCategory.FAN_LIGHT)


def is_sensor_category(category: DeviceCategory) -> bool:
    """Check if category is any type of sensor."""
    return category in (DeviceCategory.BODY_SENSOR, DeviceCategory.DOOR_SENSOR)


def is_switch_category(category: DeviceCategory) -> bool:
    """Check if category is switch or outlet."""
    return category in (DeviceCategory.SWITCH, DeviceCategory.OUTLET)


# Mapping from DeviceCategory to Home Assistant platforms
CATEGORY_TO_PLATFORMS: dict[DeviceCategory, list[str]] = {
    DeviceCategory.LIGHT: ["light"],
    DeviceCategory.FAN_LIGHT: ["light", "fan"],
    DeviceCategory.CURTAIN: ["cover"],
    DeviceCategory.SWITCH: ["switch"],
    DeviceCategory.OUTLET: ["switch"],
    DeviceCategory.HEATER: ["climate"],
    DeviceCategory.BODY_SENSOR: ["binary_sensor"],
    DeviceCategory.DOOR_SENSOR: ["binary_sensor"],
    DeviceCategory.GATEWAY: [],
    DeviceCategory.UNKNOWN: [],
}


def get_platforms_for_category(category: DeviceCategory) -> list[str]:
    """Get the Home Assistant platforms for a device category."""
    return CATEGORY_TO_PLATFORMS.get(category, [])
