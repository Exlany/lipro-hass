"""Thin state-management service for coordinator composition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

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
        return self.coordinator.devices

    def get_device(self, serial: str) -> LiproDevice | None:
        """Resolve a device by serial."""
        return self.coordinator.get_device(serial)

    def get_device_by_id(self, device_id: Any) -> LiproDevice | None:
        """Resolve a device by any known identifier."""
        return self.coordinator.get_device_by_id(device_id)
