"""Platform helper utilities for Lipro integration.

This module provides common utilities for platform setup to reduce code duplication
across light.py, switch.py, cover.py, fan.py, climate.py, etc.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.helpers.entity import Entity
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..core.coordinator import LiproDataUpdateCoordinator
    from ..core.device import LiproDevice


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


def create_platform_entities_multi[EntityT: Entity](
    coordinator: LiproDataUpdateCoordinator,
    factory_map: list[
        tuple[
            Callable[[LiproDevice], bool],
            Callable[[LiproDataUpdateCoordinator, LiproDevice], EntityT],
        ]
    ],
) -> list[EntityT]:
    """Create entities for a platform with multiple device types.

    Args:
        coordinator: The data update coordinator.
        factory_map: List of (filter, factory) tuples.

    Returns:
        List of created entities.

    Example:
        entities = create_platform_entities_multi(
            coordinator,
            [
                (lambda d: d.is_body_sensor, lambda c, d: MotionSensor(c, d)),
                (lambda d: d.is_door_sensor, lambda c, d: DoorSensor(c, d)),
            ],
        )

    """
    entities: list[EntityT] = []
    for device in coordinator.devices.values():
        for device_filter, entity_factory in factory_map:
            if device_filter(device):
                entities.append(entity_factory(coordinator, device))
    return entities


async def async_setup_platform_entities[EntityT: Entity](
    coordinator: LiproDataUpdateCoordinator,
    async_add_entities: AddEntitiesCallback,
    device_filter: Callable[[LiproDevice], bool],
    entity_factory: Callable[[LiproDataUpdateCoordinator, LiproDevice], EntityT],
) -> None:
    """Set up platform entities using a filter and factory.

    This is the async version that directly adds entities.

    Args:
        coordinator: The data update coordinator.
        async_add_entities: Callback to add entities.
        device_filter: Function that returns True for devices that should have entities.
        entity_factory: Function that creates an entity for a device.

    """
    entities = create_platform_entities(coordinator, device_filter, entity_factory)
    async_add_entities(entities)
