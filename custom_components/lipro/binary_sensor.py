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
    from .core.device import LiproDevice

# No parallel update limit needed for read-only sensors using coordinator
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro binary sensors."""
    coordinator = entry.runtime_data
    entities = [
        entity
        for device in coordinator.devices.values()
        for entity in _build_device_binary_sensors(coordinator, device)
    ]
    async_add_entities(entities)


class LiproBinarySensor(LiproEntity, BinarySensorEntity):
    """Base class for Lipro binary sensors."""


class LiproPropertyBinarySensor(LiproBinarySensor):
    """Declarative base class for property-based binary sensors.

    Subclasses only need to define class attributes:
    - _entity_suffix: Unique ID suffix for the entity
    - _device_property: The device property name to read state from
    - _invert: If True, invert the property value (default False)

    Icons are managed declaratively via icons.json (HA best practice).
    """

    _device_property: str
    _invert: bool = False

    @property
    def is_on(self) -> bool:
        """Return true if the sensor is on."""
        value = getattr(self.device, self._device_property, False)
        return not value if self._invert else bool(value)


class LiproConnectivitySensor(LiproPropertyBinarySensor):
    """Representation of a Lipro device connectivity sensor."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False  # Disabled by default
    _attr_translation_key = "connectivity"
    _entity_suffix = "connectivity"
    _device_property = "is_connected"

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Unlike other entities, the connectivity sensor should remain available
        even when the device is offline, so it can correctly report the
        disconnected (off) state instead of becoming unavailable.
        """
        return self.coordinator.last_update_success


class LiproMotionSensor(LiproPropertyBinarySensor):
    """Representation of a Lipro motion sensor."""

    _attr_device_class = BinarySensorDeviceClass.MOTION
    _attr_translation_key = "motion"
    _entity_suffix = "motion"
    _device_property = "is_activated"


class LiproDoorSensor(LiproPropertyBinarySensor):
    """Representation of a Lipro door/window sensor."""

    _attr_device_class = BinarySensorDeviceClass.DOOR
    _attr_translation_key = "door"
    _entity_suffix = "door"
    _device_property = "door_is_open"


class LiproLightLevelSensor(LiproPropertyBinarySensor):
    """Representation of a Lipro light level sensor."""

    _attr_device_class = BinarySensorDeviceClass.LIGHT
    _attr_translation_key = "light"
    # Disable by default as light level changes frequently and may be noisy
    _attr_entity_registry_enabled_default = False
    _entity_suffix = "light"
    _device_property = "is_dark"
    _invert = True


class LiproBatteryLowSensor(LiproPropertyBinarySensor):
    """Representation of a Lipro battery low sensor."""

    _attr_device_class = BinarySensorDeviceClass.BATTERY
    _attr_translation_key = "battery"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _entity_suffix = "battery_low"
    _device_property = "low_battery"


def _build_device_binary_sensors(
    coordinator,
    device: LiproDevice,
) -> list[LiproBinarySensor]:
    """Build all binary sensor entities for one device."""
    entities: list[LiproBinarySensor] = [LiproConnectivitySensor(coordinator, device)]

    if device.is_body_sensor:
        entities.extend(
            [
                LiproMotionSensor(coordinator, device),
                LiproLightLevelSensor(coordinator, device),
                LiproBatteryLowSensor(coordinator, device),
            ]
        )
    elif device.is_door_sensor:
        entities.extend(
            [
                LiproDoorSensor(coordinator, device),
                LiproLightLevelSensor(coordinator, device),
                LiproBatteryLowSensor(coordinator, device),
            ]
        )

    return entities
