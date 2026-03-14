"""Mutable device-state helpers extracted from ``LiproDevice``."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from . import state_accessors, state_getters
from .state_fields import (
    BOOL_PROPERTY_MAP,
    DEVICE_STATE_EXPORTED_ATTRIBUTES,
    INT_PROPERTY_MAP,
)


def _bool_property(attr_name: str) -> property:
    """Create one explicit boolean state property."""
    property_key = BOOL_PROPERTY_MAP[attr_name]

    def _getter(self: DeviceState) -> bool:
        return self.get_bool_property(property_key)

    return property(_getter)


def _int_property(attr_name: str) -> property:
    """Create one explicit integer state property."""
    property_key, default = INT_PROPERTY_MAP[attr_name]

    def _getter(self: DeviceState) -> int:
        return self.get_int_property(property_key, default)

    return property(_getter)


@dataclass(slots=True)
class DeviceState:
    """State/attribute helper bound to one device property mapping."""

    properties: dict[str, Any] = field(default_factory=dict)
    min_color_temp_kelvin: int = 0
    max_color_temp_kelvin: int = 0
    max_fan_gear: int = 1
    _supports_color_temp: bool = False

    @classmethod
    def from_api_data(
        cls,
        properties: Mapping[str, Any],
        *,
        min_color_temp_kelvin: int,
        max_color_temp_kelvin: int,
        max_fan_gear: int,
        supports_color_temp: bool,
    ) -> DeviceState:
        """Build state from one normalized property payload."""
        return cls(
            dict(properties),
            min_color_temp_kelvin,
            max_color_temp_kelvin,
            max_fan_gear,
            supports_color_temp,
        )

    def update_from_properties(self, properties: Mapping[str, Any]) -> None:
        """Merge new properties into the mutable device state."""
        self.properties.update(properties)

    get_property = state_getters.get_property
    get_bool_property = state_getters.get_bool_property
    get_int_property = state_getters.get_int_property
    get_float_property = state_getters.get_float_property
    get_optional_int_property = state_getters.get_optional_int_property
    get_str_property = state_getters.get_str_property
    percent_to_kelvin_for_device = state_accessors.percent_to_kelvin_for_device
    kelvin_to_percent_for_device = state_accessors.kelvin_to_percent_for_device

    is_on = _bool_property("is_on")
    fade_state = _bool_property("fade_state")
    sleep_aid_enabled = _bool_property("sleep_aid_enabled")
    wake_up_enabled = _bool_property("wake_up_enabled")
    focus_mode_enabled = _bool_property("focus_mode_enabled")
    body_reactive_enabled = _bool_property("body_reactive_enabled")
    panel_led_enabled = _bool_property("panel_led_enabled")
    panel_memory_enabled = _bool_property("panel_memory_enabled")
    panel_pair_key_full = _bool_property("panel_pair_key_full")
    ir_switch_enabled = _bool_property("ir_switch_enabled")
    is_charging = _bool_property("is_charging")
    is_moving = _bool_property("is_moving")
    fan_is_on = _bool_property("fan_is_on")
    heater_is_on = _bool_property("heater_is_on")
    door_is_open = _bool_property("door_is_open")
    is_activated = _bool_property("is_activated")
    is_dark = _bool_property("is_dark")
    low_battery = _bool_property("low_battery")

    brightness = _int_property("brightness")
    fan_mode = _int_property("fan_mode")
    heater_mode = _int_property("heater_mode")
    wind_gear = _int_property("wind_gear")
    light_mode = _int_property("light_mode")
    wind_direction_mode = _int_property("wind_direction_mode")
    aeration_gear = _int_property("aeration_gear")

    supports_color_temp = property(state_accessors.supports_color_temp)
    is_connected = property(state_accessors.is_connected)
    color_temp = property(state_accessors.color_temp)
    battery_level = property(state_accessors.battery_level)
    has_battery = property(state_accessors.has_battery)
    position = property(state_accessors.position)
    direction = property(state_accessors.direction)
    fan_gear = property(state_accessors.fan_gear)
    aeration_is_on = property(state_accessors.aeration_is_on)


__all__ = ["DEVICE_STATE_EXPORTED_ATTRIBUTES", "DeviceState"]
