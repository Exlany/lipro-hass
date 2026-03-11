"""Thin state-management service for coordinator composition."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...device import LiproDevice
    from ..coordinator import Coordinator


@dataclass(slots=True)
class CoordinatorStateService:
    """Expose coordinator state access through a service boundary."""

    coordinator: Coordinator

    @property
    def devices(self) -> dict[str, LiproDevice]:
        """Return the wrapped coordinator device mapping."""
        return self.coordinator.state_runtime.get_all_devices()  # type: ignore[no-any-return]


    def get_device(self, serial: str) -> LiproDevice | None:
        """Resolve a device by serial."""
        return self.coordinator.state_runtime.get_device_by_serial(serial)  # type: ignore[no-any-return]

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Resolve a device by any known identifier."""
        return self.coordinator.state_runtime.get_device_by_id(device_id)  # type: ignore[no-any-return]

    def get_device_lock(self, device_serial: str) -> asyncio.Lock:
        """Return the per-device update lock.

        Args:
            device_serial: Device serial number

        Returns:
            Lock for the device
        """
        device = self.get_device(device_serial)
        if device is None:
            # Return a new lock for unknown devices (shouldn't happen)
            return asyncio.Lock()
        return self.coordinator.state_runtime.get_device_lock(device)  # type: ignore[no-any-return]
