"""Coordinator device refresh service - stable read/refresh surface."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ...device import LiproDevice
    from ..runtime.device_runtime import DeviceRuntime
    from ..runtime.state_runtime import StateRuntime


@dataclass(slots=True)
class CoordinatorDeviceRefreshService:
    """Expose device lookup and full-refresh through a stable adapter."""

    device_runtime: DeviceRuntime
    state_runtime: StateRuntime
    refresh_callback: Callable[[], Awaitable[dict[str, LiproDevice]]]

    @property
    def devices(self) -> Mapping[str, LiproDevice]:
        """Return the latest read-only coordinator device map."""
        return self.state_runtime.get_all_devices()

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Resolve one device by any known coordinator identifier."""
        return self.state_runtime.get_device_by_id(device_id)

    def request_force_refresh(self) -> None:
        """Request the next refresh call to rebuild the full device snapshot."""
        self.device_runtime.request_force_refresh()

    def request_group_reconciliation(
        self,
        *,
        device_name: str,
        timestamp: float,
    ) -> None:
        """Request canonical refresh when a mesh group comes online via MQTT."""
        del device_name, timestamp
        self.request_force_refresh()

    async def async_refresh_devices(self) -> None:
        """Trigger the coordinator's canonical full-refresh path."""
        await self.refresh_callback()
