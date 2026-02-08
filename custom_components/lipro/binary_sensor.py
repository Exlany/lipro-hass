"""Binary sensor platform for Lipro integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory

from .entities.base import LiproEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry

# No parallel update limit needed for read-only sensors using coordinator
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro binary sensors."""
    coordinator = entry.runtime_data
    entities: list[LiproBinarySensor] = []

    for device in coordinator.devices.values():
        # Add connectivity sensor for all devices (diagnostic)
        entities.append(LiproConnectivitySensor(coordinator, device))

        # Body sensor creates motion, light level, and battery sensors
        if device.is_body_sensor:
            entities.extend(
                [
                    LiproMotionSensor(coordinator, device),
                    LiproLightLevelSensor(coordinator, device),
                    LiproBatteryLowSensor(coordinator, device),
                ]
            )
        # Door sensor creates door, light level, and battery sensors
        elif device.is_door_sensor:
            entities.extend(
                [
                    LiproDoorSensor(coordinator, device),
                    LiproLightLevelSensor(coordinator, device),
                    LiproBatteryLowSensor(coordinator, device),
                ]
            )

    async_add_entities(entities)


class LiproBinarySensor(LiproEntity, BinarySensorEntity):
    """Base class for Lipro binary sensors."""


class LiproPropertyBinarySensor(LiproBinarySensor):
    """Declarative base class for property-based binary sensors.

    Subclasses only need to define class attributes:
    - _entity_suffix: Unique ID suffix for the entity
    - _device_property: The device property name to read state from
    - _icon_on / _icon_off: Icons for on/off states
    - _invert: If True, invert the property value (default False)
    """

    _device_property: str
    _icon_on: str
    _icon_off: str
    _invert: bool = False

    @property
    def is_on(self) -> bool:
        """Return true if the sensor is on."""
        value = getattr(self.device, self._device_property, False)
        return not value if self._invert else bool(value)

    @property
    def icon(self) -> str:
        """Return the icon based on state."""
        return self._icon_on if self.is_on else self._icon_off


class LiproConnectivitySensor(LiproPropertyBinarySensor):
    """Representation of a Lipro device connectivity sensor."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False  # Disabled by default
    _attr_translation_key = "connectivity"
    _entity_suffix = "connectivity"
    _device_property = "is_connected"
    _icon_on = "mdi:lan-connect"
    _icon_off = "mdi:lan-disconnect"


class LiproMotionSensor(LiproPropertyBinarySensor):
    """Representation of a Lipro motion sensor."""

    _attr_device_class = BinarySensorDeviceClass.MOTION
    _attr_translation_key = "motion"
    _entity_suffix = "motion"
    _device_property = "is_activated"
    _icon_on = "mdi:motion-sensor"
    _icon_off = "mdi:motion-sensor-off"


class LiproDoorSensor(LiproPropertyBinarySensor):
    """Representation of a Lipro door/window sensor."""

    _attr_device_class = BinarySensorDeviceClass.DOOR
    _attr_translation_key = "door"
    _entity_suffix = "door"
    _device_property = "door_is_open"
    _icon_on = "mdi:door-open"
    _icon_off = "mdi:door-closed"


class LiproLightLevelSensor(LiproPropertyBinarySensor):
    """Representation of a Lipro light level sensor."""

    _attr_device_class = BinarySensorDeviceClass.LIGHT
    _attr_translation_key = "light"
    # Disable by default as light level changes frequently and may be noisy
    _attr_entity_registry_enabled_default = False
    _entity_suffix = "light"
    _device_property = "is_dark"
    _invert = True
    _icon_on = "mdi:brightness-7"
    _icon_off = "mdi:brightness-3"


class LiproBatteryLowSensor(LiproPropertyBinarySensor):
    """Representation of a Lipro battery low sensor."""

    _attr_device_class = BinarySensorDeviceClass.BATTERY
    _attr_translation_key = "battery"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _entity_suffix = "battery_low"
    _device_property = "low_battery"
    _icon_on = "mdi:battery-alert"
    _icon_off = "mdi:battery"
