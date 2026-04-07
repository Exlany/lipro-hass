# ruff: noqa: D102, D107
"""endpoint operations collaborator for the REST child façade."""

from __future__ import annotations

from typing import Protocol

from .power_service import OutletPowerInfoResult
from .status_fallback import RecordStatusBatchMetric
from .types import (
    CommandResultApiResponse,
    ConnectStatusQueryResult,
    DeviceListResponse,
    DeviceStatusItem,
    JsonObject,
    MqttConfigResponse,
    OtaInfoRow,
    ScheduleTimingRow,
)


class _DeviceEndpointsPort(Protocol):
    async def get_devices(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> DeviceListResponse: ...

    async def get_product_configs(self) -> list[JsonObject]: ...


class _StatusEndpointsPort(Protocol):
    async def query_device_status(
        self,
        device_ids: list[str],
        *,
        max_devices_per_query: int = 100,
        on_batch_metric: RecordStatusBatchMetric | None = None,
    ) -> list[DeviceStatusItem]: ...

    async def query_mesh_group_status(self, group_ids: list[str]) -> list[JsonObject]: ...

    async def query_connect_status(
        self, device_ids: list[str]
    ) -> ConnectStatusQueryResult: ...


class _CommandEndpointsPort(Protocol):
    async def send_command(
        self,
        device_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> JsonObject: ...

    async def send_group_command(
        self,
        group_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> JsonObject: ...


class _MiscEndpointsPort(Protocol):
    async def get_mqtt_config(self) -> MqttConfigResponse: ...

    async def fetch_outlet_power_info(self, device_id: str) -> OutletPowerInfoResult: ...

    async def query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: int | str,
    ) -> CommandResultApiResponse: ...

    async def get_city(self) -> JsonObject: ...

    async def query_user_cloud(self) -> JsonObject: ...

    async def query_ota_info(
        self,
        device_id: str,
        device_type: int | str,
        *,
        iot_name: str | None = None,
        allow_rich_v2_fallback: bool = False,
    ) -> list[OtaInfoRow]: ...

    async def fetch_body_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> JsonObject: ...

    async def fetch_door_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> JsonObject: ...


class _ScheduleEndpointsPort(Protocol):
    async def get_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]: ...

    async def add_device_schedule(
        self,
        device_id: str,
        device_type: int | str,
        days: list[int],
        times: list[int],
        events: list[int],
        group_id: str = "",
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]: ...

    async def delete_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        schedule_ids: list[int],
        group_id: str = "",
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]: ...

class RestEndpointSurface:
    """Group endpoint operations away from the REST façade root body."""

    def __init__(
        self,
        *,
        device_endpoints: _DeviceEndpointsPort,
        status_endpoints: _StatusEndpointsPort,
        command_endpoints: _CommandEndpointsPort,
        misc_endpoints: _MiscEndpointsPort,
        schedule_endpoints: _ScheduleEndpointsPort,
    ) -> None:
        self._device_endpoints = device_endpoints
        self._status_endpoints = status_endpoints
        self._command_endpoints = command_endpoints
        self._misc_endpoints = misc_endpoints
        self._schedule_endpoints = schedule_endpoints

    async def get_devices(self, offset: int = 0, limit: int = 100) -> DeviceListResponse:
        return await self._device_endpoints.get_devices(offset=offset, limit=limit)

    async def get_product_configs(self) -> list[JsonObject]:
        return await self._device_endpoints.get_product_configs()

    async def query_device_status(
        self,
        device_ids: list[str],
        *,
        max_devices_per_query: int = 100,
        on_batch_metric: RecordStatusBatchMetric | None = None,
    ) -> list[DeviceStatusItem]:
        return await self._status_endpoints.query_device_status(
            device_ids,
            max_devices_per_query=max_devices_per_query,
            on_batch_metric=on_batch_metric,
        )

    async def query_mesh_group_status(
        self,
        group_ids: list[str],
    ) -> list[JsonObject]:
        return await self._status_endpoints.query_mesh_group_status(group_ids)

    async def query_connect_status(
        self, device_ids: list[str]
    ) -> ConnectStatusQueryResult:
        return await self._status_endpoints.query_connect_status(device_ids)

    async def send_command(
        self,
        device_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> JsonObject:
        return await self._command_endpoints.send_command(
            device_id=device_id,
            command=command,
            device_type=device_type,
            properties=properties,
            iot_name=iot_name,
        )

    async def send_group_command(
        self,
        group_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> JsonObject:
        return await self._command_endpoints.send_group_command(
            group_id=group_id,
            command=command,
            device_type=device_type,
            properties=properties,
            iot_name=iot_name,
        )

    async def get_mqtt_config(self) -> MqttConfigResponse:
        return await self._misc_endpoints.get_mqtt_config()

    async def fetch_outlet_power_info(self, device_id: str) -> OutletPowerInfoResult:
        return await self._misc_endpoints.fetch_outlet_power_info(device_id)

    async def query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: int | str,
    ) -> CommandResultApiResponse:
        return await self._misc_endpoints.query_command_result(
            msg_sn=msg_sn,
            device_id=device_id,
            device_type=device_type,
        )

    async def get_city(self) -> JsonObject:
        return await self._misc_endpoints.get_city()

    async def query_user_cloud(self) -> JsonObject:
        return await self._misc_endpoints.query_user_cloud()

    async def query_ota_info(
        self,
        device_id: str,
        device_type: int | str,
        *,
        iot_name: str | None = None,
        allow_rich_v2_fallback: bool = False,
    ) -> list[OtaInfoRow]:
        return await self._misc_endpoints.query_ota_info(
            device_id=device_id,
            device_type=device_type,
            iot_name=iot_name,
            allow_rich_v2_fallback=allow_rich_v2_fallback,
        )

    async def fetch_body_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> JsonObject:
        return await self._misc_endpoints.fetch_body_sensor_history(
            device_id=device_id,
            device_type=device_type,
            sensor_device_id=sensor_device_id,
            mesh_type=mesh_type,
        )

    async def fetch_door_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> JsonObject:
        return await self._misc_endpoints.fetch_door_sensor_history(
            device_id=device_id,
            device_type=device_type,
            sensor_device_id=sensor_device_id,
            mesh_type=mesh_type,
        )

    async def get_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        return await self._schedule_endpoints.get_device_schedules(
            device_id=device_id,
            device_type=device_type,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

    async def add_device_schedule(
        self,
        device_id: str,
        device_type: int | str,
        days: list[int],
        times: list[int],
        events: list[int],
        group_id: str = "",
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        return await self._schedule_endpoints.add_device_schedule(
            device_id=device_id,
            device_type=device_type,
            days=days,
            times=times,
            events=events,
            group_id=group_id,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

    async def delete_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        schedule_ids: list[int],
        group_id: str = "",
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        return await self._schedule_endpoints.delete_device_schedules(
            device_id=device_id,
            device_type=device_type,
            schedule_ids=schedule_ids,
            group_id=group_id,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

__all__ = ["RestEndpointSurface"]
