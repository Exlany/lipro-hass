"""State reader for device state queries and lookups."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ....device import LiproDevice
    from ....device.identity_index import DeviceIdentityIndex


class StateReader:
    """Read-only state access for device queries and lookups."""

    def __init__(
        self,
        *,
        devices: dict[str, LiproDevice],
        device_identity_index: DeviceIdentityIndex,
    ) -> None:
        """Initialize state reader."""
        self._devices = devices
        self._device_identity_index = device_identity_index

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Look up a device by any known identifier."""
        return self._device_identity_index.get(device_id)

    def get_device_by_serial(self, serial: str) -> LiproDevice | None:
        """Look up a device by serial number."""
        return self._devices.get(serial)

    def get_all_devices(self) -> Mapping[str, LiproDevice]:
        """Return a read-only device mapping view."""
        return MappingProxyType(self._devices)

    def get_device_count(self) -> int:
        """Return total device count."""
        return len(self._devices)

    def get_online_device_count(self) -> int:
        """Return count of online devices."""
        return sum(1 for device in self._devices.values() if device.is_online)

    def get_devices_by_room(self, room_id: int | str) -> list[LiproDevice]:
        """Return all devices associated with a room id.

        The Lipro API exposes room ids as ints, but tests and legacy mocks may
        provide non-numeric strings. This helper stays defensive by supporting
        both representations.
        """
        room_int: int | None
        room_str: str | None

        if isinstance(room_id, int):
            room_int = room_id
            room_str = None
        else:
            normalized = room_id.strip()
            room_str = normalized or None
            room_int = int(normalized) if normalized.isdigit() else None

        devices: list[LiproDevice] = []
        for device in self._devices.values():
            value = getattr(device, "room_id", None)
            if (room_int is not None and value == room_int) or (
                room_str is not None and str(value) == room_str
            ):
                devices.append(device)

        return devices

    def has_device(self, device_id: str) -> bool:
        """Return True when a device identifier is known."""
        return self.get_device_by_id(device_id) is not None


__all__ = ["StateReader"]
