"""Coordinator schedule service - formal runtime surface for schedule operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...api.types import ScheduleTimingRow
    from .protocol_service import CoordinatorProtocolService, ScheduleMeshDeviceLike


@dataclass(slots=True)
class CoordinatorScheduleService:
    """Expose schedule operations through one runtime-owned service surface."""

    protocol_service: CoordinatorProtocolService

    async def async_get_schedules(
        self,
        device: ScheduleMeshDeviceLike,
    ) -> list[ScheduleTimingRow]:
        """Return schedules for one runtime device."""
        return await self.protocol_service.async_get_device_schedules_for_device(device)

    async def async_add_schedule(
        self,
        device: ScheduleMeshDeviceLike,
        days: list[int],
        times: list[int],
        events: list[int],
    ) -> list[ScheduleTimingRow]:
        """Create one schedule for one runtime device."""
        return await self.protocol_service.async_add_device_schedule_for_device(
            device,
            days,
            times,
            events,
        )

    async def async_delete_schedules(
        self,
        device: ScheduleMeshDeviceLike,
        schedule_ids: list[int],
    ) -> list[ScheduleTimingRow]:
        """Delete schedules for one runtime device."""
        return await self.protocol_service.async_delete_device_schedules_for_device(
            device,
            schedule_ids,
        )


__all__ = ["CoordinatorScheduleService"]
