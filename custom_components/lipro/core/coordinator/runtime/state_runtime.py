"""State runtime implementation with dependency injection."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from .state import StateIndexManager, StateReader, StateUpdater

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from ...device import LiproDevice
    from ...device.identity_index import DeviceIdentityIndex
    from ..entity_protocol import LiproEntityProtocol

_LOGGER = logging.getLogger(__name__)


class StateRuntime:
    """Standalone state runtime with no coordinator dependency."""

    def __init__(
        self,
        *,
        devices: dict[str, LiproDevice],
        device_identity_index: DeviceIdentityIndex,
        entities: dict[str, LiproEntityProtocol],
        entities_by_device: dict[str, list[LiproEntityProtocol]],
        normalize_device_key: Callable[[str], str],
    ) -> None:
        """Initialize state runtime.

        Args:
            devices: Device dictionary keyed by serial
            device_identity_index: Identity index for multi-key lookups
            entities: Entity registry keyed by entity_id
            entities_by_device: Entity index keyed by normalized device key
            normalize_device_key: Function to normalize device identifiers
        """
        self._reader = StateReader(
            devices=devices,
            device_identity_index=device_identity_index,
        )
        self._updater = StateUpdater(
            devices=devices,
            entities_by_device=entities_by_device,
            normalize_device_key=normalize_device_key,
        )
        self._index_manager = StateIndexManager(
            device_identity_index=device_identity_index,
            entities=entities,
            entities_by_device=entities_by_device,
            normalize_device_key=normalize_device_key,
        )

    # Reader methods
    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Look up a device by any known identifier."""
        return self._reader.get_device_by_id(device_id)

    def get_device_by_serial(self, serial: str) -> LiproDevice | None:
        """Look up a device by serial number."""
        return self._reader.get_device_by_serial(serial)

    def get_all_devices(self) -> Mapping[str, LiproDevice]:
        """Get a read-only view of all devices."""
        return self._reader.get_all_devices()

    def get_device_count(self) -> int:
        """Get total device count."""
        return self._reader.get_device_count()

    def get_online_device_count(self) -> int:
        """Get count of online devices."""
        return self._reader.get_online_device_count()

    def get_devices_by_room(self, room_id: int) -> list[LiproDevice]:
        """Get all devices in a specific room."""
        return self._reader.get_devices_by_room(room_id)

    def get_device_lock(self, device: LiproDevice) -> asyncio.Lock:
        """Return the per-device property update lock.

        Exposed so the service layer can coordinate updates without reaching into
        private runtime internals.
        """
        return self._updater.get_device_lock(device)

    def has_device(self, device_id: str) -> bool:
        """Check if a device exists."""
        return self._reader.has_device(device_id)

    # Updater methods
    async def apply_properties_update(
        self,
        device: LiproDevice,
        properties: dict[str, Any],
        *,
        source: str = "unknown",
    ) -> bool:
        """Apply property updates to a device and notify entities."""
        return await self._updater.apply_properties_update(device, properties, source=source)


    async def batch_update_properties(
        self,
        updates: list[tuple[LiproDevice, dict[str, Any]]],
        *,
        source: str = "batch",
    ) -> int:
        """Apply property updates to multiple devices."""
        return await self._updater.batch_update_properties(updates, source=source)

    # Index manager methods
    def rebuild_device_index(self, devices: dict[str, LiproDevice]) -> None:
        """Rebuild device identity index from current device snapshot."""
        self._index_manager.rebuild_device_index(devices)

    def register_entity(
        self,
        entity: LiproEntityProtocol,
        device_serial: str,
    ) -> None:
        """Register an entity for state update notifications."""
        self._index_manager.register_entity(entity, device_serial)

    def unregister_entity(self, entity_id: str) -> None:
        """Unregister the active entity for one entity ID."""
        self._index_manager.unregister_entity(entity_id)

    def unregister_entity_instance(self, entity: object) -> None:
        """Remove one entity instance while preserving active-instance semantics."""
        self._index_manager.unregister_entity_instance(entity)

    def get_entity_count(self) -> int:
        """Get total registered entity count."""
        return self._index_manager.get_entity_count()

    def get_entities_for_device(self, device_serial: str) -> list[LiproEntityProtocol]:
        """Get all entities associated with a device."""
        return self._index_manager.get_entities_for_device(device_serial)


__all__ = ["StateRuntime"]
