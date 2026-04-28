"""Immutable capability projections for Lipro devices."""

from __future__ import annotations

from dataclasses import dataclass

from ...const.categories import DeviceCategory


@dataclass(frozen=True, slots=True)
class CapabilitySnapshot:
    """Stable device capability truth derived from normalized metadata."""

    device_type_hex: str
    category: DeviceCategory
    supports_color_temp: bool
    max_fan_gear: int = 1
    min_color_temp_kelvin: int = 0
    max_color_temp_kelvin: int = 0

    @property
    def is_light(self) -> bool:
        """Return whether the device is a light."""
        return self.category == DeviceCategory.LIGHT

    @property
    def is_fan_light(self) -> bool:
        """Return whether the device is a fan light."""
        return self.category == DeviceCategory.FAN_LIGHT

    @property
    def is_curtain(self) -> bool:
        """Return whether the device is a curtain."""
        return self.category == DeviceCategory.CURTAIN

    @property
    def is_switch(self) -> bool:
        """Return whether the device is a switch-family device."""
        return self.category in (DeviceCategory.SWITCH, DeviceCategory.OUTLET)

    @property
    def is_outlet(self) -> bool:
        """Return whether the device is an outlet."""
        return self.category == DeviceCategory.OUTLET

    @property
    def is_heater(self) -> bool:
        """Return whether the device is a heater."""
        return self.category == DeviceCategory.HEATER

    @property
    def is_sensor(self) -> bool:
        """Return whether the device is a supported sensor."""
        return self.category in (DeviceCategory.BODY_SENSOR, DeviceCategory.DOOR_SENSOR)

    @property
    def is_body_sensor(self) -> bool:
        """Return whether the device is a body sensor."""
        return self.category == DeviceCategory.BODY_SENSOR

    @property
    def is_door_sensor(self) -> bool:
        """Return whether the device is a door sensor."""
        return self.category == DeviceCategory.DOOR_SENSOR

    @property
    def is_gateway(self) -> bool:
        """Return whether the device is a gateway."""
        return self.category == DeviceCategory.GATEWAY

    @property
    def is_panel(self) -> bool:
        """Return whether the device is a switch-panel device."""
        return self.category == DeviceCategory.SWITCH


__all__ = ["CapabilitySnapshot"]
