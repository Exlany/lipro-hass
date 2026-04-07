"""Host-neutral device category enumeration for Lipro integration."""

from __future__ import annotations

from enum import Enum, auto
from functools import cache

__all__ = [
    'DeviceCategory',
    'get_device_category',
    'is_light_category',
    'is_sensor_category',
    'is_switch_category',
]


class DeviceCategory(Enum):
    """Device category enumeration derived from normalized device metadata."""

    LIGHT = auto()
    FAN_LIGHT = auto()
    CURTAIN = auto()
    SWITCH = auto()
    OUTLET = auto()
    HEATER = auto()
    BODY_SENSOR = auto()
    DOOR_SENSOR = auto()
    GATEWAY = auto()
    UNKNOWN = auto()


@cache
def _get_device_category_map() -> dict[str, DeviceCategory]:
    """Build and cache the device type to category mapping."""
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
    """Return the normalized host-neutral category for one device type hex."""
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
