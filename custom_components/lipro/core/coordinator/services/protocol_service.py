"""Coordinator protocol-facing service surface."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...api.types import OtaInfoRow, ScheduleTimingRow
    from ...protocol import LiproProtocolFacade


@dataclass(slots=True)
class CoordinatorProtocolService:
    """Expose protocol-facing runtime operations through one formal service."""

    protocol_getter: Callable[[], LiproProtocolFacade]

    async def async_get_device_schedules(
        self,
        device_id: str,
        device_type: str | int,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        """Query schedules through the formal protocol surface."""
        return await self.protocol_getter().get_device_schedules(
            device_id,
            device_type,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=list(mesh_member_ids or []),
        )

    async def async_add_device_schedule(
        self,
        device_id: str,
        device_type: str | int,
        days: list[int],
        times: list[int],
        events: list[int],
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        """Create a schedule through the formal protocol surface."""
        return await self.protocol_getter().add_device_schedule(
            device_id,
            device_type,
            days,
            times,
            events,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=list(mesh_member_ids or []),
        )

    async def async_delete_device_schedules(
        self,
        device_id: str,
        device_type: str | int,
        schedule_ids: list[int],
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        """Delete schedules through the formal protocol surface."""
        return await self.protocol_getter().delete_device_schedules(
            device_id,
            device_type,
            schedule_ids,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=list(mesh_member_ids or []),
        )

    async def async_query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: str | int,
    ) -> Any:
        """Query command-result diagnostics through the formal protocol surface."""
        return await self.protocol_getter().query_command_result(
            msg_sn=msg_sn,
            device_id=device_id,
            device_type=device_type,
        )

    async def async_get_city(self) -> dict[str, object]:
        """Query city metadata through the formal protocol surface."""
        return dict(await self.protocol_getter().get_city())

    async def async_query_user_cloud(self) -> dict[str, object]:
        """Query user-cloud metadata through the formal protocol surface."""
        return dict(await self.protocol_getter().query_user_cloud())

    async def async_fetch_body_sensor_history(
        self,
        *,
        device_id: str,
        device_type: str | int,
        sensor_device_id: str,
        mesh_type: str,
    ) -> dict[str, object]:
        """Query body-sensor history through the formal protocol surface."""
        return dict(
            await self.protocol_getter().fetch_body_sensor_history(
                device_id=device_id,
                device_type=device_type,
                sensor_device_id=sensor_device_id,
                mesh_type=mesh_type,
            )
        )

    async def async_fetch_door_sensor_history(
        self,
        *,
        device_id: str,
        device_type: str | int,
        sensor_device_id: str,
        mesh_type: str,
    ) -> dict[str, object]:
        """Query door-sensor history through the formal protocol surface."""
        return dict(
            await self.protocol_getter().fetch_door_sensor_history(
                device_id=device_id,
                device_type=device_type,
                sensor_device_id=sensor_device_id,
                mesh_type=mesh_type,
            )
        )

    async def async_query_ota_info(
        self,
        *,
        device_id: str,
        device_type: str | int,
        iot_name: str | None,
        allow_rich_v2_fallback: bool,
    ) -> list[OtaInfoRow]:
        """Query OTA metadata through the formal protocol surface."""
        return await self.protocol_getter().query_ota_info(
            device_id=device_id,
            device_type=device_type,
            iot_name=iot_name,
            allow_rich_v2_fallback=allow_rich_v2_fallback,
        )

    async def async_fetch_outlet_power_info(self, device_id: str) -> object:
        """Query outlet-power info through the formal protocol surface."""
        return await self.protocol_getter().fetch_outlet_power_info(device_id)


__all__ = ["CoordinatorProtocolService"]
