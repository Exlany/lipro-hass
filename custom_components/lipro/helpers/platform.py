"""Platform helper utilities for Lipro integration.

This module provides common utilities for platform setup to reduce code duplication
across light.py, switch.py, cover.py, fan.py, climate.py, etc.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence

    from homeassistant.helpers.entity import Entity

    from ..core.coordinator import LiproDataUpdateCoordinator
    from ..core.device import LiproDevice

    type DevicePredicate = Callable[[LiproDevice], bool]
    type DeviceEntityFactory[EntityT: Entity] = Callable[
        [LiproDataUpdateCoordinator, LiproDevice], EntityT
    ]
    type DeviceEntityRule[EntityT: Entity] = tuple[
        DevicePredicate, Sequence[DeviceEntityFactory[EntityT]]
    ]


def create_platform_entities[EntityT: Entity](
    coordinator: LiproDataUpdateCoordinator,
    device_filter: Callable[[LiproDevice], bool],
    entity_factory: Callable[[LiproDataUpdateCoordinator, LiproDevice], EntityT],
) -> list[EntityT]:
    """Create entities for a platform using a filter and factory function.

    This is a helper function to reduce boilerplate in platform setup.

    Args:
        coordinator: The data update coordinator.
        device_filter: Function that returns True for devices that should have entities.
        entity_factory: Function that creates an entity for a device.

    Returns:
        List of created entities.

    Example:
        entities = create_platform_entities(
            coordinator,
            device_filter=lambda d: d.is_light,
            entity_factory=lambda c, d: LiproLight(c, d),
        )

    """
    return [
        entity_factory(coordinator, device)
        for device in coordinator.devices.values()
        if device_filter(device)
    ]


def create_device_entities[EntityT: Entity](
    coordinator: LiproDataUpdateCoordinator,
    entity_builder: Callable[
        [LiproDataUpdateCoordinator, LiproDevice],
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
    coordinator: LiproDataUpdateCoordinator,
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
