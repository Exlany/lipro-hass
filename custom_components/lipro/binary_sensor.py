"""Binary sensor platform for Lipro integration."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory

from .entities.base import LiproEntity
from .helpers.platform import (
    add_entry_entities,
    build_device_entities_from_rules,
    create_device_entities,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry
    from .core.device import LiproDevice
    from .runtime_types import LiproRuntimeCoordinator

StateReader = Callable[[object], object]

# No parallel update limit needed for read-only sensors using coordinator
PARALLEL_UPDATES = 0


def _read_is_connected(device: LiproDevice) -> object:
    """Read connectivity truth from the formal device state."""
    return device.state.is_connected


def _read_is_activated(device: LiproDevice) -> object:
    """Read motion-activation truth from the formal device state."""
    return device.state.is_activated


def _read_door_is_open(device: LiproDevice) -> object:
    """Read door-open truth from the formal device state."""
    return device.state.door_is_open


def _read_is_dark(device: LiproDevice) -> object:
    """Read darkness truth from the formal device state."""
    return device.state.is_dark


def _read_low_battery(device: LiproDevice) -> object:
    """Read low-battery truth from the formal device state."""
    return device.state.low_battery


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro binary sensors."""
    add_entry_entities(
        entry,
        async_add_entities,
        entity_builder=lambda coordinator: create_device_entities(
            coordinator,
            _build_device_binary_sensors,
        ),
    )


class LiproBinarySensor(LiproEntity, BinarySensorEntity):
    """Base class for Lipro binary sensors."""


class LiproPropertyBinarySensor(LiproBinarySensor):
    """Declarative base class for property-based binary sensors."""

    state_reader: StateReader
    _invert: bool = False

    @property
    def is_on(self) -> bool:
        """Return true if the sensor is on."""
        value = type(self).state_reader(self.device)
        return not value if self._invert else bool(value)


class LiproConnectivitySensor(LiproPropertyBinarySensor):
    """Representation of a Lipro device connectivity sensor."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _attr_translation_key = "connectivity"
    _entity_suffix = "connectivity"
    state_reader = _read_is_connected

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success


class LiproMotionSensor(LiproPropertyBinarySensor):
    """Representation of a Lipro motion sensor."""

    _attr_device_class = BinarySensorDeviceClass.MOTION
    _attr_translation_key = "motion"
    _entity_suffix = "motion"
    state_reader = _read_is_activated


class LiproDoorSensor(LiproPropertyBinarySensor):
    """Representation of a Lipro door/window sensor."""

    _attr_device_class = BinarySensorDeviceClass.DOOR
    _attr_translation_key = "door"
    _entity_suffix = "door"
    state_reader = _read_door_is_open


class LiproLightLevelSensor(LiproPropertyBinarySensor):
    """Representation of a Lipro light level sensor."""

    _attr_device_class = BinarySensorDeviceClass.LIGHT
    _attr_translation_key = "light"
    _attr_entity_registry_enabled_default = False
    _entity_suffix = "light"
    state_reader = _read_is_dark
    _invert = True


class LiproBatteryLowSensor(LiproPropertyBinarySensor):
    """Representation of a Lipro battery low sensor."""

    _attr_device_class = BinarySensorDeviceClass.BATTERY
    _attr_translation_key = "battery"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _entity_suffix = "battery_low"
    state_reader = _read_low_battery


def _build_device_binary_sensors(
    coordinator: LiproRuntimeCoordinator,
    device: LiproDevice,
) -> list[LiproBinarySensor]:
    """Build all binary sensor entities for one device."""
    return build_device_entities_from_rules(
        coordinator,
        device,
        always_factories=(LiproConnectivitySensor,),
        rules=(
            (
                lambda d: d.capabilities.is_body_sensor,
                (LiproMotionSensor, LiproLightLevelSensor, LiproBatteryLowSensor),
            ),
            (
                lambda d: (
                    d.capabilities.is_door_sensor and not d.capabilities.is_body_sensor
                ),
                (LiproDoorSensor, LiproLightLevelSensor, LiproBatteryLowSensor),
            ),
        ),
    )
