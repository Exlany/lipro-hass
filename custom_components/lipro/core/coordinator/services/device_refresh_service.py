"""Coordinator device refresh service - API stability layer.

This service provides a stable facade over the device runtime, implementing
the Stable Interface Pattern from Clean Architecture.

Design rationale:
- **API Stability**: Isolates Entity layer from DeviceRuntime implementation changes
- **Dependency Inversion**: Entity depends on Service interface, not Runtime
- **Single Responsibility**: Focused on device refresh coordination

Architecture role:
- NOT a business logic layer (logic lives in DeviceRuntime)
- NOT a data loader (DeviceRuntime handles that)
- IS a stable API boundary (protects Entity layer from Runtime refactoring)

This is intentional "thin proxy" design - the value is in API stability,
not in adding refresh complexity.
"""

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
        return self.coordinator.state_runtime.get_all_devices()  # type: ignore[no-any-return]

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Resolve one device by any known coordinator identifier."""
        return self.coordinator.state_runtime.get_device_by_id(device_id)  # type: ignore[no-any-return]

    async def async_refresh_devices(self) -> None:
        """Trigger a forced device refresh on the wrapped coordinator.

        This method triggers the coordinator's full update cycle, which includes:
        1. Calling device_runtime.refresh_devices(force=True)
        2. Syncing the snapshot back to coordinator._state.devices
        3. Notifying all entities via async_set_updated_data()

        This ensures proper state synchronization and entity updates.
        """
        await self.coordinator.async_request_refresh()
