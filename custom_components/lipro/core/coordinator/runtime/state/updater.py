"""State updater for device property updates and notifications."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from ....device import LiproDevice
    from ...entity_protocol import LiproEntityProtocol

_LOGGER = logging.getLogger(__name__)


class StateUpdater:
    """Manage device state updates and entity notifications."""

    def __init__(
        self,
        devices: dict[str, LiproDevice],
        entities_by_device: dict[str, list[LiproEntityProtocol]],
        normalize_device_key: Callable[[str], str],
    ) -> None:
        """Initialize state updater.

        Args:
            devices: Device dictionary keyed by serial
            entities_by_device: Entity index keyed by normalized device key
            normalize_device_key: Function to normalize device identifiers
        """
        self._devices = devices
        self._entities_by_device = entities_by_device
        self._normalize_device_key = normalize_device_key
        # Lock per device to protect concurrent property updates
        self._device_locks: dict[str, asyncio.Lock] = {}

    def _get_device_lock(self, device: LiproDevice) -> asyncio.Lock:
        """Get or create lock for a specific device.

        Args:
            device: Target device

        Returns:
            Lock for the device
        """
        if device.serial not in self._device_locks:
            self._device_locks[device.serial] = asyncio.Lock()
        return self._device_locks[device.serial]

    async def apply_properties_update(
        self,
        device: LiproDevice,
        properties: dict[str, Any],
        *,
        source: str = "unknown",
    ) -> bool:
        """Apply property updates to a device and notify entities.

        Args:
            device: Target device
            properties: Property updates to apply
            source: Update source for logging (mqtt/rest/command)

        Returns:
            True if any properties changed
        """
        if not properties:
            return False

        lock = self._get_device_lock(device)
        async with lock:
            device.update_properties(properties)
            changed = True

            if changed:
                _LOGGER.debug(
                    "Applied %d property updates to %s from %s",
                    len(properties),
                    device.name,
                    source,
                )
                self._notify_device_entities(device)

        return changed

    def update_device_online_status(
        self,
        device: LiproDevice,
        is_online: bool,
    ) -> bool:
        """Update device online status.

        Args:
            device: Target device
            is_online: New online status

        Returns:
            True if status changed
        """
        # Simplified: always notify
        _LOGGER.debug(
            "Device %s online status update: %s",
            device.name,
            "online" if is_online else "offline",
        )
        self._notify_device_entities(device)
        return True

    async def batch_update_properties(
        self,
        updates: list[tuple[LiproDevice, dict[str, Any]]],
        *,
        source: str = "batch",
    ) -> int:
        """Apply property updates to multiple devices.

        Args:
            updates: List of (device, properties) tuples
            source: Update source for logging

        Returns:
            Number of devices that changed
        """
        changed_count = 0
        for device, properties in updates:
            if await self.apply_properties_update(device, properties, source=source):
                changed_count += 1

        if changed_count:
            _LOGGER.debug(
                "Batch update from %s changed %d/%d devices",
                source,
                changed_count,
                len(updates),
            )

        return changed_count

    def _notify_device_entities(self, device: LiproDevice) -> None:
        """Notify all entities associated with a device.

        Args:
            device: Device that changed
        """
        device_key = self._normalize_device_key(device.serial)
        entities = self._entities_by_device.get(device_key, [])

        for entity in entities:
            # Call method dynamically to avoid type checking issues
            if hasattr(entity, "async_write_ha_state"):
                entity.async_write_ha_state()  # type: ignore[attr-defined]

        if entities:
            _LOGGER.debug(
                "Notified %d entities for device %s",
                len(entities),
                device.name,
            )


__all__ = ["StateUpdater"]
