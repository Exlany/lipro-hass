"""Platform helper utilities for Lipro integration.

This module provides common utilities for platform setup to reduce code duplication
across light.py, switch.py, cover.py, fan.py, climate.py, etc.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence

    from homeassistant.helpers.entity import Entity

    from ..core.device import LiproDevice
    from ..runtime_types import LiproCoordinator

    type DevicePredicate = Callable[[LiproDevice], bool]
    type DeviceEntityFactory[EntityT: Entity] = Callable[
        [LiproCoordinator, LiproDevice], EntityT
    ]
    type DeviceEntityRule[EntityT: Entity] = tuple[
        DevicePredicate, Sequence[DeviceEntityFactory[EntityT]]
    ]


def create_platform_entities[EntityT: Entity](
    coordinator: LiproCoordinator,
    device_filter: Callable[[LiproDevice], bool],
    entity_factory: Callable[[LiproCoordinator, LiproDevice], EntityT],
) -> list[EntityT]:
    """Create entities for a platform using a filter and factory function."""
    return [
        entity_factory(coordinator, device)
        for device in coordinator.devices.values()
        if device_filter(device)
    ]


def create_device_entities[EntityT: Entity](
    coordinator: LiproCoordinator,
    entity_builder: Callable[
        [LiproCoordinator, LiproDevice],
        Iterable[EntityT],
    ],
    *,
    device_filter: Callable[[LiproDevice], bool] | None = None,
) -> list[EntityT]:
    """Create one or more entities per device using a shared builder."""
    entities: list[EntityT] = []
    for device in coordinator.devices.values():
        if device_filter is not None and not device_filter(device):
            continue
        entities.extend(entity_builder(coordinator, device))
    return entities


def build_device_entities_from_rules[EntityT: Entity](
    coordinator: LiproCoordinator,
    device: LiproDevice,
    *,
    rules: Sequence[DeviceEntityRule[EntityT]],
    always_factories: Sequence[DeviceEntityFactory[EntityT]] = (),
) -> list[EntityT]:
    """Build entities for one device from declarative conditional rules."""
    entities = [factory(coordinator, device) for factory in always_factories]
    for predicate, factories in rules:
        if not predicate(device):
            continue
        entities.extend(factory(coordinator, device) for factory in factories)
    return entities


def device_has_raw_property(device: LiproDevice, property_key: str) -> bool:
    """Return whether the normalized device payload explicitly includes a property."""
    return property_key in device.properties


def should_expose_light_property_switch(
    device: LiproDevice,
    *,
    property_key: str,
) -> bool:
    """Return whether one light-only supplemental switch should be exposed."""
    return device.capabilities.is_light and device_has_raw_property(device, property_key)


def should_expose_panel_property_switch(
    device: LiproDevice,
    *,
    property_key: str,
) -> bool:
    """Return whether one panel-only supplemental switch should be exposed."""
    return device.capabilities.is_panel and device_has_raw_property(device, property_key)


def should_expose_light_gear_select(device: LiproDevice) -> bool:
    """Return whether one light should expose the gear select surface."""
    return device.capabilities.is_light and device.has_gear_presets


def should_expose_firmware_update_entity(device: LiproDevice) -> bool:
    """Return whether one device qualifies for the firmware update platform."""
    return not device.is_group and device.has_valid_iot_id
