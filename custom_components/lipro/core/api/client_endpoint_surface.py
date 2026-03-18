# ruff: noqa: D102,D107,SLF001
"""Endpoint-forwarding collaborator for the REST child façade."""

from __future__ import annotations

from typing import Any, Protocol, cast

from .power_service import OutletPowerInfoResult
from .types import DeviceListResponse, OtaInfoRow, ScheduleTimingRow


class _EndpointSurfacePort(Protocol):
    _device_endpoints: Any
    _status_endpoints: Any
    _command_endpoints: Any
    _misc_endpoints: Any
    _schedule_endpoints: Any


class ClientEndpointSurface:
    """Group endpoint forwarding away from the REST façade root body."""

    def __init__(self, client: _EndpointSurfacePort) -> None:
        self._client = client

    async def get_devices(self, offset: int = 0, limit: int = 100) -> DeviceListResponse:
        return cast(
            DeviceListResponse,
            await self._client._device_endpoints.get_devices(offset=offset, limit=limit),
        )

    async def get_product_configs(self) -> list[dict[str, Any]]:
        return cast(
            list[dict[str, Any]],
            await self._client._device_endpoints.get_product_configs(),
        )

    async def query_device_status(
        self,
        device_ids: list[str],
        *,
        max_devices_per_query: int = 100,
        on_batch_metric: Any = None,
    ) -> list[dict[str, Any]]:
        return cast(
            list[dict[str, Any]],
            await self._client._status_endpoints.query_device_status(
            device_ids,
            max_devices_per_query=max_devices_per_query,
            on_batch_metric=on_batch_metric,
            ),
        )

    async def query_mesh_group_status(
        self,
        group_ids: list[str],
    ) -> list[dict[str, Any]]:
        return cast(
            list[dict[str, Any]],
            await self._client._status_endpoints.query_mesh_group_status(group_ids),
        )

    async def query_connect_status(self, device_ids: list[str]) -> dict[str, bool]:
        return cast(
            dict[str, bool],
            await self._client._status_endpoints.query_connect_status(device_ids),
        )

    async def send_command(
        self,
        device_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self._client._command_endpoints.send_command(
            device_id=device_id,
            command=command,
            device_type=device_type,
            properties=properties,
            iot_name=iot_name,
            ),
        )

    async def send_group_command(
        self,
        group_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self._client._command_endpoints.send_group_command(
            group_id=group_id,
            command=command,
            device_type=device_type,
            properties=properties,
            iot_name=iot_name,
            ),
        )

    async def get_mqtt_config(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self._client._misc_endpoints.get_mqtt_config())

    async def fetch_outlet_power_info(self, device_id: str) -> OutletPowerInfoResult:
        return cast(
            OutletPowerInfoResult,
            await self._client._misc_endpoints.fetch_outlet_power_info(device_id),
        )

    async def query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: int | str,
    ) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self._client._misc_endpoints.query_command_result(
            msg_sn=msg_sn,
            device_id=device_id,
            device_type=device_type,
            ),
        )

    async def get_city(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self._client._misc_endpoints.get_city())

    async def query_user_cloud(self) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self._client._misc_endpoints.query_user_cloud(),
        )

    async def query_ota_info(
        self,
        device_id: str,
        device_type: int | str,
        *,
        iot_name: str | None = None,
        allow_rich_v2_fallback: bool = False,
    ) -> list[OtaInfoRow]:
        return cast(
            list[OtaInfoRow],
            await self._client._misc_endpoints.query_ota_info(
            device_id=device_id,
            device_type=device_type,
            iot_name=iot_name,
            allow_rich_v2_fallback=allow_rich_v2_fallback,
            ),
        )

    async def fetch_body_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self._client._misc_endpoints.fetch_body_sensor_history(
            device_id=device_id,
            device_type=device_type,
            sensor_device_id=sensor_device_id,
            mesh_type=mesh_type,
            ),
        )

    async def fetch_door_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self._client._misc_endpoints.fetch_door_sensor_history(
            device_id=device_id,
            device_type=device_type,
            sensor_device_id=sensor_device_id,
            mesh_type=mesh_type,
            ),
        )

    async def get_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        return cast(
            list[ScheduleTimingRow],
            await self._client._schedule_endpoints.get_device_schedules(
            device_id=device_id,
            device_type=device_type,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
            ),
        )

    async def add_device_schedule(
        self,
        device_id: str,
        device_type: int | str,
        days: list[int],
        times: list[int],
        events: list[int],
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        return cast(
            list[ScheduleTimingRow],
            await self._client._schedule_endpoints.add_device_schedule(
            device_id=device_id,
            device_type=device_type,
            days=days,
            times=times,
            events=events,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
            ),
        )

    async def delete_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        schedule_ids: list[int],
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        return cast(
            list[ScheduleTimingRow],
            await self._client._schedule_endpoints.delete_device_schedules(
            device_id=device_id,
            device_type=device_type,
            schedule_ids=schedule_ids,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
            ),
        )


__all__ = ["ClientEndpointSurface"]
