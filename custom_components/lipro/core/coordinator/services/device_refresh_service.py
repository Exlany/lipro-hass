"""Coordinator device-refresh service boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...device import LiproDevice
    from ..coordinator import Coordinator


@dataclass(slots=True)
class CoordinatorDeviceRefreshService:
    """Expose device lookup/refresh through a composition-friendly adapter."""

    coordinator: Coordinator

    @property
    def devices(self) -> dict[str, LiproDevice]:
        """Return the wrapped coordinator device map."""
        return self.coordinator.state_runtime.get_all_devices()

    def get_device_by_id(self, device_id: object) -> LiproDevice | None:
        """Resolve one device by any known coordinator identifier."""
        return self.coordinator.state_runtime.get_device_by_id(str(device_id))

    async def async_refresh_devices(self) -> None:
        """Trigger a forced device refresh on the wrapped coordinator."""
        await self.coordinator.device_runtime.refresh_devices(force=True)
