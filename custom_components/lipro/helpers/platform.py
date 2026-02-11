"""Platform helper utilities for Lipro integration.

This module provides common utilities for platform setup to reduce code duplication
across light.py, switch.py, cover.py, fan.py, climate.py, etc.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.helpers.entity import Entity

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
