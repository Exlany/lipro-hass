"""Derived category and capability snapshot for one Lipro device."""

from __future__ import annotations

from dataclasses import dataclass

from ...const.categories import DeviceCategory, get_device_category


@dataclass(frozen=True)
class DeviceCapabilities:
    """Derived device category and capability flags."""

    device_type_hex: str
    category: DeviceCategory
    supports_color_temp: bool

    @property
    def is_light(self) -> bool:
        """Return True when the device is a light."""
        return self.category == DeviceCategory.LIGHT

    @property
    def is_fan_light(self) -> bool:
        """Return True when the device is a fan light."""
        return self.category == DeviceCategory.FAN_LIGHT

    @property
    def is_curtain(self) -> bool:
        """Return True when the device is a curtain."""
        return self.category == DeviceCategory.CURTAIN

    @property
    def is_switch(self) -> bool:
        """Return True when the device is a switch or outlet."""
        return self.category in (DeviceCategory.SWITCH, DeviceCategory.OUTLET)

    @property
    def is_outlet(self) -> bool:
        """Return True when the device is an outlet."""
        return self.category == DeviceCategory.OUTLET

    @property
    def is_heater(self) -> bool:
        """Return True when the device is a heater."""
        return self.category == DeviceCategory.HEATER

    @property
    def is_sensor(self) -> bool:
        """Return True when the device is a supported sensor."""
        return self.category in (DeviceCategory.BODY_SENSOR, DeviceCategory.DOOR_SENSOR)

    @property
    def is_body_sensor(self) -> bool:
        """Return True when the device is a body sensor."""
        return self.category == DeviceCategory.BODY_SENSOR

    @property
    def is_door_sensor(self) -> bool:
        """Return True when the device is a door sensor."""
        return self.category == DeviceCategory.DOOR_SENSOR

    @property
    def is_gateway(self) -> bool:
        """Return True when the device is a gateway."""
        return self.category == DeviceCategory.GATEWAY

    @classmethod
    def from_device_profile(
        cls,
        *,
        device_type_hex: str,
        min_color_temp_kelvin: int,
        max_color_temp_kelvin: int,
    ) -> DeviceCapabilities:
        """Build capabilities from device profile metadata."""
        return cls(
            device_type_hex=device_type_hex,
            category=get_device_category(device_type_hex),
            supports_color_temp=(
                max_color_temp_kelvin > 0 and min_color_temp_kelvin > 0
            ),
        )


__all__ = ["DeviceCapabilities"]
