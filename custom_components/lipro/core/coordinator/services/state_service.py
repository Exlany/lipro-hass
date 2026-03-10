"""Thin state-management service for coordinator composition."""

from __future__ import annotations

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
        return self.coordinator._state_runtime.get_all_devices()

    def get_device(self, serial: str) -> LiproDevice | None:
        """Resolve a device by serial."""
        return self.coordinator._state_runtime.get_device_by_serial(serial)

    def get_device_by_id(self, device_id: object) -> LiproDevice | None:
        """Resolve a device by any known identifier."""
        return self.coordinator._state_runtime.get_device_by_id(device_id)
