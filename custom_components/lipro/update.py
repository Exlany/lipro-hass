"""Firmware update platform for Lipro integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .entities.firmware_update import LiproFirmwareUpdateEntity
from .helpers.platform import (
    create_platform_entities,
    should_expose_firmware_update_entity,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro firmware update entities."""
    entities = create_platform_entities(
        entry.runtime_data,
        should_expose_firmware_update_entity,
        LiproFirmwareUpdateEntity,
    )
    async_add_entities(entities)
