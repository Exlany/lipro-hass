"""State index manager for device identity and entity tracking."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from ....device import LiproDevice
    from ....device.identity_index import DeviceIdentityIndex
    from ...entity_protocol import LiproEntityProtocol

_LOGGER = logging.getLogger(__name__)


class StateIndexManager:
    """Manage device identity index and entity registration."""

    def __init__(
        self,
        device_identity_index: DeviceIdentityIndex,
        entities: dict[str, LiproEntityProtocol],
        entities_by_device: dict[str, list[LiproEntityProtocol]],
        normalize_device_key: Callable[[str], str],
    ) -> None:
        """Initialize state index manager.

        Args:
            device_identity_index: Identity index for multi-key lookups
            entities: Entity registry keyed by entity_id
            entities_by_device: Entity index keyed by normalized device key
            normalize_device_key: Function to normalize device identifiers
        """
        self._device_identity_index = device_identity_index
        self._entities = entities
        self._entities_by_device = entities_by_device
        self._normalize_device_key = normalize_device_key

    def rebuild_device_index(self, devices: dict[str, LiproDevice]) -> None:
        """Rebuild device identity index from current device snapshot.

        Args:
            devices: Current device dictionary
        """
        self._device_identity_index.clear()
        for device in devices.values():
            self._device_identity_index.register(device.serial, device)

        _LOGGER.debug(
            "Rebuilt device identity index with %d devices",
            len(devices),
        )

    def register_entity(
        self,
        entity: LiproEntityProtocol,
        device_serial: str,
    ) -> None:
        """Register an entity for state update notifications.

        Args:
            entity: Entity to register
            device_serial: Associated device serial
        """
        # Use hasattr to avoid type checking issues
        if not hasattr(entity, "entity_id"):
            _LOGGER.warning("Entity missing entity_id attribute")
            return

        entity_id = entity.entity_id  # type: ignore[attr-defined]
        if entity_id in self._entities:
            _LOGGER.warning(
                "Entity %s already registered, replacing",
                entity_id,
            )

        self._entities[entity_id] = entity

        device_key = self._normalize_device_key(device_serial)
        if device_key not in self._entities_by_device:
            self._entities_by_device[device_key] = []

        if entity not in self._entities_by_device[device_key]:
            self._entities_by_device[device_key].append(entity)

        _LOGGER.debug(
            "Registered entity %s for device %s",
            entity_id,
            device_serial,
        )

    def unregister_entity(self, entity_id: str) -> None:
        """Unregister an entity.

        Args:
            entity_id: Entity identifier to remove
        """
        entity = self._entities.pop(entity_id, None)
        if entity is None:
            return

        # Remove from device index
        for device_entities in self._entities_by_device.values():
            if entity in device_entities:
                device_entities.remove(entity)

        _LOGGER.debug("Unregistered entity %s", entity_id)

    def get_entity_count(self) -> int:
        """Get total registered entity count.

        Returns:
            Number of registered entities
        """
        return len(self._entities)

    def get_entities_for_device(self, device_serial: str) -> list[LiproEntityProtocol]:
        """Get all entities associated with a device.

        Args:
            device_serial: Device serial number

        Returns:
            List of entities for the device
        """
        device_key = self._normalize_device_key(device_serial)
        return self._entities_by_device.get(device_key, [])


__all__ = ["StateIndexManager"]
