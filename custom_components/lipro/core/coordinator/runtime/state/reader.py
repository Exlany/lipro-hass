"""State reader for device state queries and lookups."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ....device import LiproDevice
    from ....device.identity_index import DeviceIdentityIndex

_LOGGER = logging.getLogger(__name__)


class StateReader:
    """Read-only state access for device queries and lookups."""

    def __init__(
        self,
        devices: dict[str, LiproDevice],
        device_identity_index: DeviceIdentityIndex,
    ) -> None:
        """Initialize state reader.

        Args:
            devices: Device dictionary keyed by serial
            device_identity_index: Identity index for multi-key lookups
        """
        self._devices = devices
        self._device_identity_index = device_identity_index

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Look up a device by any known identifier.

        Args:
            device_id: Device serial, MAC, or other identifier

        Returns:
            Device instance or None if not found
        """
        return self._device_identity_index.get(device_id)

    def get_device_by_serial(self, serial: str) -> LiproDevice | None:
        """Look up a device by serial number.

        Args:
            serial: Device serial number

        Returns:
            Device instance or None if not found
        """
        return self._devices.get(serial)

    def get_all_devices(self) -> dict[str, LiproDevice]:
        """Get all devices.

        Returns:
            Dictionary of devices keyed by serial
        """
        return self._devices

    def get_device_count(self) -> int:
        """Get total device count.

        Returns:
            Number of devices
        """
        return len(self._devices)

    def get_online_device_count(self) -> int:
        """Get count of online devices.

        Returns:
            Number of online devices
        """
        # Simplified: count devices with state.online property
        count = 0
        for device in self._devices.values():
            if hasattr(device, "state") and hasattr(device.state, "online"):
                if device.state.online:  # type: ignore[attr-defined]
                    count += 1
        return count

    def get_devices_by_room(self, room_id: str) -> list[LiproDevice]:
        """Get all devices in a specific room.

        Args:
            room_id: Room identifier

        Returns:
            List of devices in the room
        """
        return [
            device
            for device in self._devices.values()
            if hasattr(device, "room_id") and device.room_id == room_id  # type: ignore[attr-defined]
        ]

    def has_device(self, device_id: str) -> bool:
        """Check if a device exists.

        Args:
            device_id: Device serial or identifier

        Returns:
            True if device exists
        """
        return self.get_device_by_id(device_id) is not None


__all__ = ["StateReader"]
