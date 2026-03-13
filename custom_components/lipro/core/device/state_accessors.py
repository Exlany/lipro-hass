"""Derived state accessors reused by ``DeviceState``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...const.properties import (
    DEFAULT_COLOR_TEMP_PERCENT,
    PROP_BATTERY,
    PROP_CONNECT_STATE,
    PROP_DIRECTION,
    PROP_FAN_GEAR,
    PROP_POSITION,
    PROP_TEMPERATURE,
)
from .state_fields import BOOL_PROPERTY_MAP, INT_PROPERTY_MAP
from .state_math import (
    direction_to_ha,
    kelvin_to_percent_for_bounds,
    percent_to_kelvin_for_bounds,
)

if TYPE_CHECKING:
    from .state import DeviceState


def percent_to_kelvin_for_device(self: DeviceState, percent: int) -> int:
    """Convert API percentage to Kelvin using device-specific bounds."""
    return percent_to_kelvin_for_bounds(
        percent,
        min_color_temp_kelvin=self.min_color_temp_kelvin,
        max_color_temp_kelvin=self.max_color_temp_kelvin,
    )


def kelvin_to_percent_for_device(self: DeviceState, kelvin: int) -> int:
    """Convert Kelvin back to API percentage."""
    return kelvin_to_percent_for_bounds(
        kelvin,
        min_color_temp_kelvin=self.min_color_temp_kelvin,
        max_color_temp_kelvin=self.max_color_temp_kelvin,
    )


def supports_color_temp(self: DeviceState) -> bool:
    """Return whether color temperature adjustment is supported."""
    return self._supports_color_temp


def is_connected(self: DeviceState) -> bool:
    """Return whether the device is connected."""
    return self.get_bool_property(PROP_CONNECT_STATE, True)


def color_temp(self: DeviceState) -> int:
    """Return color temperature in Kelvin."""
    return self.percent_to_kelvin_for_device(
        self.get_int_property(PROP_TEMPERATURE, DEFAULT_COLOR_TEMP_PERCENT)
    )


def battery_level(self: DeviceState) -> int | None:
    """Return battery level or ``None`` when absent."""
    return self.get_optional_int_property(PROP_BATTERY)


def has_battery(self: DeviceState) -> bool:
    """Return whether battery telemetry exists."""
    return PROP_BATTERY in self.properties


def position(self: DeviceState) -> int:
    """Return curtain position in the 0-100 range."""
    return max(0, min(100, self.get_int_property(PROP_POSITION, 0)))


def direction(self: DeviceState) -> str | None:
    """Return curtain direction in HA-friendly strings."""
    return direction_to_ha(self.get_property(PROP_DIRECTION))


def fan_gear(self: DeviceState) -> int:
    """Return fan gear clamped to the device range."""
    return max(1, min(self.max_fan_gear, self.get_int_property(PROP_FAN_GEAR, 1)))


def aeration_is_on(self: DeviceState) -> bool:
    """Return whether aeration is enabled."""
    return self.get_int_property(INT_PROPERTY_MAP["aeration_gear"][0], 0) > 0


def resolve_state_attribute(self: DeviceState, name: str) -> object:
    """Resolve simple derived state attributes lazily."""
    if name in BOOL_PROPERTY_MAP:
        return self.get_bool_property(BOOL_PROPERTY_MAP[name])
    if name in INT_PROPERTY_MAP:
        key, default = INT_PROPERTY_MAP[name]
        return self.get_int_property(key, default)
    msg = f"{type(self).__name__!s} has no attribute {name!r}"
    raise AttributeError(msg)


__all__ = [
    "aeration_is_on",
    "battery_level",
    "color_temp",
    "direction",
    "fan_gear",
    "has_battery",
    "is_connected",
    "kelvin_to_percent_for_device",
    "percent_to_kelvin_for_device",
    "position",
    "resolve_state_attribute",
    "supports_color_temp",
]
