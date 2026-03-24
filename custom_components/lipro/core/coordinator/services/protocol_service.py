"""Coordinator protocol-facing service surface."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, cast

from ...api.types import DiagnosticsApiResponse
from ...command.result import CommandResultPayload
from ...utils.identifiers import normalize_iot_device_id

if TYPE_CHECKING:
    from ...api.types import OtaInfoRow, ScheduleTimingRow
    from ...protocol import LiproProtocolFacade
from ...protocol.contracts import OutletPowerInfoResult


class ScheduleMeshDeviceLike(Protocol):
    """Minimal device surface required by schedule protocol helpers."""

    @property
    def iot_device_id(self) -> str: ...

    @property
    def device_type_hex(self) -> str: ...

    @property
    def mesh_gateway_device_id(self) -> str | None: ...

    @property
    def mesh_group_member_ids(self) -> list[str]: ...

    @property
    def ir_remote_gateway_device_id(self) -> str | None: ...


def build_schedule_mesh_context(
    device: ScheduleMeshDeviceLike,
) -> tuple[str, list[str]]:
    """Normalize mesh gateway/member metadata for schedule protocol calls."""
    gateway_candidate = device.mesh_gateway_device_id
    if gateway_candidate is None:
        gateway_candidate = device.ir_remote_gateway_device_id
    mesh_gateway_id = normalize_iot_device_id(gateway_candidate) or ""

    mesh_member_ids: list[str] = []
    seen_member_ids: set[str] = set()
    for member_id in device.mesh_group_member_ids:
        normalized = normalize_iot_device_id(member_id)
        if normalized is None or normalized in seen_member_ids:
            continue
        seen_member_ids.add(normalized)
        mesh_member_ids.append(normalized)

    return mesh_gateway_id, mesh_member_ids


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

    async def async_get_device_schedules_for_device(
        self,
        device: ScheduleMeshDeviceLike,
    ) -> list[ScheduleTimingRow]:
        """Query schedules using the device-owned protocol context."""
        mesh_gateway_id, mesh_member_ids = build_schedule_mesh_context(device)
        return await self.async_get_device_schedules(
            device.iot_device_id,
            device.device_type_hex,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
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

    async def async_add_device_schedule_for_device(
        self,
        device: ScheduleMeshDeviceLike,
        days: list[int],
        times: list[int],
        events: list[int],
    ) -> list[ScheduleTimingRow]:
        """Create a schedule using the device-owned protocol context."""
        mesh_gateway_id, mesh_member_ids = build_schedule_mesh_context(device)
        return await self.async_add_device_schedule(
            device.iot_device_id,
            device.device_type_hex,
            days,
            times,
            events,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
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

    async def async_delete_device_schedules_for_device(
        self,
        device: ScheduleMeshDeviceLike,
        schedule_ids: list[int],
    ) -> list[ScheduleTimingRow]:
        """Delete schedules using the device-owned protocol context."""
        mesh_gateway_id, mesh_member_ids = build_schedule_mesh_context(device)
        return await self.async_delete_device_schedules(
            device.iot_device_id,
            device.device_type_hex,
            schedule_ids,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

    async def async_query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: str | int,
    ) -> CommandResultPayload:
        """Query command-result diagnostics through the formal protocol surface."""
        return cast(
            CommandResultPayload,
            await self.protocol_getter().query_command_result(
                msg_sn=msg_sn,
                device_id=device_id,
                device_type=device_type,
            ),
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
    ) -> DiagnosticsApiResponse:
        """Query body-sensor history through the formal protocol surface."""
        return cast(
            DiagnosticsApiResponse,
            dict(
                await self.protocol_getter().fetch_body_sensor_history(
                    device_id=device_id,
                    device_type=device_type,
                    sensor_device_id=sensor_device_id,
                    mesh_type=mesh_type,
                )
            ),
        )

    async def async_fetch_door_sensor_history(
        self,
        *,
        device_id: str,
        device_type: str | int,
        sensor_device_id: str,
        mesh_type: str,
    ) -> DiagnosticsApiResponse:
        """Query door-sensor history through the formal protocol surface."""
        return cast(
            DiagnosticsApiResponse,
            dict(
                await self.protocol_getter().fetch_door_sensor_history(
                    device_id=device_id,
                    device_type=device_type,
                    sensor_device_id=sensor_device_id,
                    mesh_type=mesh_type,
                )
            ),
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

    async def async_fetch_outlet_power_info(self, device_id: str) -> OutletPowerInfoResult:
        """Query outlet-power info through the formal protocol surface."""
        return await self.protocol_getter().fetch_outlet_power_info(device_id)


__all__ = ["CoordinatorProtocolService", "build_schedule_mesh_context"]
