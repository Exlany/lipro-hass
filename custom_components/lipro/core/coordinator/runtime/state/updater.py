"""State updater for device property updates and notifications."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from ...types import PropertyDict

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
        self._device_locks: dict[str, asyncio.Lock] = {}

    def _get_device_lock(self, device: LiproDevice) -> asyncio.Lock:
        """Get or create lock for a specific device."""
        if device.serial not in self._device_locks:
            self._device_locks[device.serial] = asyncio.Lock()
        return self._device_locks[device.serial]

    def get_device_lock(self, device: LiproDevice) -> asyncio.Lock:
        """Return the per-device property update lock."""
        return self._get_device_lock(device)

    async def apply_properties_update(
        self,
        device: LiproDevice,
        properties: PropertyDict,
        *,
        source: str = "unknown",
        skip_protected: bool = True,
    ) -> bool:
        """Apply property updates to a device and notify entities.

        Returns:
            True if any properties changed
        """
        if not properties:
            return False

        lock = self._get_device_lock(device)
        async with lock:
            if skip_protected:
                properties = self._filter_protected_properties(device, properties)
                if not properties:
                    _LOGGER.debug(
                        "All properties for %s are debounce-protected, skipping update from %s",
                        device.name,
                        source,
                    )
                    return False

            device.update_properties(properties)
            if source == "mqtt":
                device.mark_mqtt_update()
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


    async def batch_update_properties(
        self,
        updates: list[tuple[LiproDevice, PropertyDict]],
        *,
        source: str = "batch",
    ) -> int:
        """Apply property updates to multiple devices."""
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

    def _filter_protected_properties(
        self,
        device: LiproDevice,
        properties: PropertyDict,
    ) -> PropertyDict:
        """Filter out properties that are currently protected by debounce."""
        device_key = self._normalize_device_key(device.serial)
        entities = self._entities_by_device.get(device_key, [])

        protected_keys: set[str] = set()
        for entity in entities:
            protected_keys.update(entity.get_protected_keys())

        if not protected_keys:
            return properties

        filtered = {k: v for k, v in properties.items() if k not in protected_keys}

        if len(filtered) < len(properties):
            _LOGGER.debug(
                "Filtered %d protected properties for %s: %s",
                len(properties) - len(filtered),
                device.name,
                protected_keys & properties.keys(),
            )

        return filtered

    def _notify_device_entities(self, device: LiproDevice) -> None:
        """Notify all entities associated with a device."""
        device_key = self._normalize_device_key(device.serial)
        entities = self._entities_by_device.get(device_key, [])

        for entity in entities:
            entity.async_write_ha_state()

        if entities:
            _LOGGER.debug(
                "Notified %d entities for device %s",
                len(entities),
                device.name,
            )


__all__ = ["StateUpdater"]
