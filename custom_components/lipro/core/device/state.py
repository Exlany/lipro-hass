"""Mutable device-state helpers extracted from ``LiproDevice``."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, ClassVar

from . import state_accessors, state_getters
from .state_fields import DEVICE_STATE_EXPORTED_ATTRIBUTES


@dataclass(slots=True)
class DeviceState:
    """State/attribute helper bound to one device property mapping."""

    properties: dict[str, Any] = field(default_factory=dict)
    min_color_temp_kelvin: int = 0
    max_color_temp_kelvin: int = 0
    max_fan_gear: int = 1
    _supports_color_temp: bool = False
    _exposed_attributes: ClassVar[tuple[str, ...]] = DEVICE_STATE_EXPORTED_ATTRIBUTES

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
    supports_color_temp = property(state_accessors.supports_color_temp)
    is_connected = property(state_accessors.is_connected)
    color_temp = property(state_accessors.color_temp)
    battery_level = property(state_accessors.battery_level)
    has_battery = property(state_accessors.has_battery)
    position = property(state_accessors.position)
    direction = property(state_accessors.direction)
    fan_gear = property(state_accessors.fan_gear)
    aeration_is_on = property(state_accessors.aeration_is_on)

    def __getattr__(self, name: str) -> Any:
        """Resolve simple derived state attributes lazily."""
        return state_accessors.resolve_state_attribute(self, name)


__all__ = ["DEVICE_STATE_EXPORTED_ATTRIBUTES", "DeviceState"]
