"""Firmware update platform for Lipro integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .entities.firmware_update import LiproFirmwareUpdateEntity

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
    coordinator = entry.runtime_data
    entities = [
        LiproFirmwareUpdateEntity(coordinator, device)
        for device in coordinator.devices.values()
        if not device.is_group and device.has_valid_iot_id
    ]
    async_add_entities(entities)
