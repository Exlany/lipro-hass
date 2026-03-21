"""Public endpoint-operation surface for `LiproRestFacade`.

Endpoint operations live here as static bound methods so the composition root
does not have to carry every explicit endpoint wrapper implementation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .power_service import OutletPowerInfoResult
from .status_fallback import RecordStatusBatchMetric
from .types import (
    CommandResultApiResponse,
    DeviceListResponse,
    DeviceStatusItem,
    JsonObject,
    MqttConfigResponse,
    OtaInfoRow,
    ScheduleTimingRow,
)

if TYPE_CHECKING:
    from .rest_facade import LiproRestFacade


async def get_devices(
    self: LiproRestFacade,
    offset: int = 0,
    limit: int = 100,
) -> DeviceListResponse:
    """Return canonical device rows through the explicit device endpoint."""
    return await self._endpoint_surface.get_devices(offset=offset, limit=limit)


async def get_product_configs(self: LiproRestFacade) -> list[JsonObject]:
    """Return canonical product configuration rows."""
    return await self._endpoint_surface.get_product_configs()


async def query_device_status(
    self: LiproRestFacade,
    device_ids: list[str],
    *,
    max_devices_per_query: int = 100,
    on_batch_metric: RecordStatusBatchMetric | None = None,
) -> list[DeviceStatusItem]:
    """Return canonical device-status rows through the explicit status endpoint."""
    return await self._endpoint_surface.query_device_status(
        device_ids,
        max_devices_per_query=max_devices_per_query,
        on_batch_metric=on_batch_metric,
    )


async def query_mesh_group_status(
    self: LiproRestFacade,
    group_ids: list[str],
) -> list[JsonObject]:
    """Return canonical mesh-group status rows."""
    return await self._endpoint_surface.query_mesh_group_status(group_ids)


async def query_connect_status(
    self: LiproRestFacade,
    device_ids: list[str],
) -> dict[str, bool]:
    """Return connectivity status for the requested devices."""
    return await self._endpoint_surface.query_connect_status(device_ids)


async def send_command(
    self: LiproRestFacade,
    device_id: str,
    command: str,
    device_type: int | str,
    properties: list[dict[str, str]] | None = None,
    iot_name: str = "",
) -> JsonObject:
    """Send one device command through the explicit command endpoint."""
    return await self._endpoint_surface.send_command(
        device_id=device_id,
        command=command,
        device_type=device_type,
        properties=properties,
        iot_name=iot_name,
    )


async def send_group_command(
    self: LiproRestFacade,
    group_id: str,
    command: str,
    device_type: int | str,
    properties: list[dict[str, str]] | None = None,
    iot_name: str = "",
) -> JsonObject:
    """Send one group command through the explicit command endpoint."""
    return await self._endpoint_surface.send_group_command(
        group_id=group_id,
        command=command,
        device_type=device_type,
        properties=properties,
        iot_name=iot_name,
    )


async def get_mqtt_config(self: LiproRestFacade) -> MqttConfigResponse:
    """Return MQTT configuration through the explicit misc endpoint."""
    return await self._endpoint_surface.get_mqtt_config()


async def fetch_outlet_power_info(
    self: LiproRestFacade,
    device_id: str,
) -> OutletPowerInfoResult:
    """Return outlet power information for one device."""
    return await self._endpoint_surface.fetch_outlet_power_info(device_id)


async def query_command_result(
    self: LiproRestFacade,
    *,
    msg_sn: str,
    device_id: str,
    device_type: int | str,
) -> CommandResultApiResponse:
    """Return the command-result payload for one message serial number."""
    return await self._endpoint_surface.query_command_result(
        msg_sn=msg_sn,
        device_id=device_id,
        device_type=device_type,
    )


async def get_city(self: LiproRestFacade) -> JsonObject:
    """Return the current city capability payload."""
    return await self._endpoint_surface.get_city()


async def query_user_cloud(self: LiproRestFacade) -> JsonObject:
    """Return the user-cloud capability payload."""
    return await self._endpoint_surface.query_user_cloud()


async def query_ota_info(
    self: LiproRestFacade,
    device_id: str,
    device_type: int | str,
    *,
    iot_name: str | None = None,
    allow_rich_v2_fallback: bool = False,
) -> list[OtaInfoRow]:
    """Return OTA metadata for one device through the explicit misc endpoint."""
    return await self._endpoint_surface.query_ota_info(
        device_id=device_id,
        device_type=device_type,
        iot_name=iot_name,
        allow_rich_v2_fallback=allow_rich_v2_fallback,
    )


async def fetch_body_sensor_history(
    self: LiproRestFacade,
    device_id: str,
    device_type: int | str,
    sensor_device_id: str,
    mesh_type: str,
) -> JsonObject:
    """Return body-sensor history through the explicit misc endpoint."""
    return await self._endpoint_surface.fetch_body_sensor_history(
        device_id=device_id,
        device_type=device_type,
        sensor_device_id=sensor_device_id,
        mesh_type=mesh_type,
    )


async def fetch_door_sensor_history(
    self: LiproRestFacade,
    device_id: str,
    device_type: int | str,
    sensor_device_id: str,
    mesh_type: str,
) -> JsonObject:
    """Return door-sensor history through the explicit misc endpoint."""
    return await self._endpoint_surface.fetch_door_sensor_history(
        device_id=device_id,
        device_type=device_type,
        sensor_device_id=sensor_device_id,
        mesh_type=mesh_type,
    )


async def get_device_schedules(
    self: LiproRestFacade,
    device_id: str,
    device_type: int | str,
    *,
    mesh_gateway_id: str = "",
    mesh_member_ids: list[str] | None = None,
) -> list[ScheduleTimingRow]:
    """Return device schedules through the explicit schedule endpoint."""
    return await self._endpoint_surface.get_device_schedules(
        device_id=device_id,
        device_type=device_type,
        mesh_gateway_id=mesh_gateway_id,
        mesh_member_ids=mesh_member_ids,
    )


async def add_device_schedule(
    self: LiproRestFacade,
    device_id: str,
    device_type: int | str,
    days: list[int],
    times: list[int],
    events: list[int],
    *,
    mesh_gateway_id: str = "",
    mesh_member_ids: list[str] | None = None,
) -> list[ScheduleTimingRow]:
    """Add schedules through the explicit schedule endpoint."""
    return await self._endpoint_surface.add_device_schedule(
        device_id=device_id,
        device_type=device_type,
        days=days,
        times=times,
        events=events,
        mesh_gateway_id=mesh_gateway_id,
        mesh_member_ids=mesh_member_ids,
    )


async def delete_device_schedules(
    self: LiproRestFacade,
    device_id: str,
    device_type: int | str,
    schedule_ids: list[int],
    *,
    mesh_gateway_id: str = "",
    mesh_member_ids: list[str] | None = None,
) -> list[ScheduleTimingRow]:
    """Delete schedules through the explicit schedule endpoint."""
    return await self._endpoint_surface.delete_device_schedules(
        device_id=device_id,
        device_type=device_type,
        schedule_ids=schedule_ids,
        mesh_gateway_id=mesh_gateway_id,
        mesh_member_ids=mesh_member_ids,
    )
