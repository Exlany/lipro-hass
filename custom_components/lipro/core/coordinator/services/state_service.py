"""Coordinator state service - stable device/state access surface."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...device import LiproDevice
    from ..runtime.state_runtime import StateRuntime


@dataclass(slots=True)
class CoordinatorStateService:
    """Expose state access without leaking runtime registry details."""

    state_runtime: StateRuntime

    @property
    def devices(self) -> dict[str, LiproDevice]:
        """Return the latest device mapping."""
        return self.state_runtime.get_all_devices()

    def get_device(self, serial: str) -> LiproDevice | None:
        """Resolve a device by serial."""
        return self.state_runtime.get_device_by_serial(serial)

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Resolve a device by any known identifier."""
        return self.state_runtime.get_device_by_id(device_id)

    def get_device_lock(self, device_serial: str) -> asyncio.Lock:
        """Return the canonical per-device update lock."""
        device = self.get_device(device_serial)
        if device is None:
            return asyncio.Lock()
        return self.state_runtime.get_device_lock(device)
