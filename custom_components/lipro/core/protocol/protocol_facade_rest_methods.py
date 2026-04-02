"""Support-only REST child-facing method surface for `LiproProtocolFacade`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..api.types import (
    CommandResultApiResponse,
    ConnectStatusQueryResult,
    JsonObject,
    LoginResponse,
    OtaInfoRow,
    ScheduleTimingRow,
)
from .contracts import (
    CanonicalDeviceListPage,
    CanonicalDeviceStatusRow,
    CanonicalMeshGroupStatusRow,
    CanonicalMqttConfig,
    OutletPowerInfoResult,
)
from .rest_port import StatusBatchMetric, TokenRefreshCallback

if TYPE_CHECKING:
    from .facade import LiproProtocolFacade


def set_tokens(
    self: LiproProtocolFacade,
    access_token: str,
    refresh_token: str,
    user_id: int | None = None,
    biz_id: str | None = None,
) -> None:
    """Set protocol tokens through the auth child-facing port."""
    self._rest_ports.auth.set_tokens(
        access_token,
        refresh_token,
        user_id=user_id,
        biz_id=biz_id,
    )


def set_token_refresh_callback(
    self: LiproProtocolFacade,
    callback: TokenRefreshCallback,
) -> None:
    """Register the token-refresh callback on the auth child-facing port."""
    self._rest_ports.auth.set_token_refresh_callback(callback)


async def login(
    self: LiproProtocolFacade,
    phone: str,
    password: str,
    *,
    password_is_hashed: bool = False,
) -> LoginResponse:
    """Run the formal login call through the auth child-facing port."""
    return await self._rest_ports.auth.login(
        phone,
        password,
        password_is_hashed=password_is_hashed,
    )


async def refresh_access_token(self: LiproProtocolFacade) -> LoginResponse:
    """Refresh access token through the auth child-facing port."""
    return await self._rest_ports.auth.refresh_access_token()


async def get_devices(
    self: LiproProtocolFacade,
    offset: int = 0,
    limit: int = 100,
) -> CanonicalDeviceListPage:
    """Return canonical device rows from the inventory child-facing port."""
    payload = await self._rest_ports.inventory.get_devices(offset=offset, limit=limit)
    return self.contracts.normalize_device_list_page(payload, offset=offset)


async def get_product_configs(self: LiproProtocolFacade) -> list[JsonObject]:
    """Return canonical product-configuration rows."""
    return await self._rest_ports.inventory.get_product_configs()


async def query_device_status(
    self: LiproProtocolFacade,
    device_ids: list[str],
    *,
    max_devices_per_query: int = 100,
    on_batch_metric: StatusBatchMetric | None = None,
) -> list[CanonicalDeviceStatusRow]:
    """Query device status through the status child-facing port."""
    payload = await self._rest_ports.status.query_device_status(
        device_ids,
        max_devices_per_query=max_devices_per_query,
        on_batch_metric=on_batch_metric,
    )
    return self.contracts.normalize_device_status_rows(payload)


async def query_mesh_group_status(
    self: LiproProtocolFacade,
    group_ids: list[str],
) -> list[CanonicalMeshGroupStatusRow]:
    """Query mesh-group status through the status child-facing port."""
    payload = await self._rest_ports.status.query_mesh_group_status(group_ids)
    return self.contracts.normalize_mesh_group_status_rows(payload)


async def query_connect_status(
    self: LiproProtocolFacade,
    device_ids: list[str],
) -> ConnectStatusQueryResult:
    """Query connectivity through the status child-facing port."""
    return await self._rest_ports.status.query_connect_status(device_ids)


async def send_command(
    self: LiproProtocolFacade,
    device_id: str,
    command: str,
    device_type: int | str,
    properties: list[dict[str, str]] | None = None,
    iot_name: str = "",
) -> JsonObject:
    """Send one device command through the command child-facing port."""
    return await self._rest_ports.command.send_command(
        device_id,
        command,
        device_type,
        properties=properties,
        iot_name=iot_name,
    )


async def send_group_command(
    self: LiproProtocolFacade,
    group_id: str,
    command: str,
    device_type: int | str,
    properties: list[dict[str, str]] | None = None,
    iot_name: str = "",
) -> JsonObject:
    """Send one group command through the command child-facing port."""
    return await self._rest_ports.command.send_group_command(
        group_id,
        command,
        device_type,
        properties=properties,
        iot_name=iot_name,
    )


async def get_mqtt_config(self: LiproProtocolFacade) -> CanonicalMqttConfig:
    """Fetch MQTT credentials through the misc child-facing port."""
    payload = await self._rest_ports.misc.get_mqtt_config()
    return self.contracts.normalize_mqtt_config(payload)


async def fetch_outlet_power_info(
    self: LiproProtocolFacade,
    device_id: str,
) -> OutletPowerInfoResult:
    """Fetch outlet power info through the command child-facing port."""
    return await self._rest_ports.command.fetch_outlet_power_info(device_id)


async def query_command_result(
    self: LiproProtocolFacade,
    *,
    msg_sn: str,
    device_id: str,
    device_type: int | str,
) -> CommandResultApiResponse:
    """Query command-result payload through the command child-facing port."""
    return await self._rest_ports.command.query_command_result(
        msg_sn=msg_sn,
        device_id=device_id,
        device_type=device_type,
    )


async def get_city(self: LiproProtocolFacade) -> JsonObject:
    """Fetch city metadata through the misc child-facing port."""
    return await self._rest_ports.misc.get_city()


async def query_user_cloud(self: LiproProtocolFacade) -> JsonObject:
    """Fetch user-cloud diagnostics through the misc child-facing port."""
    return await self._rest_ports.misc.query_user_cloud()


async def query_ota_info(
    self: LiproProtocolFacade,
    device_id: str,
    device_type: int | str,
    *,
    iot_name: str | None = None,
    allow_rich_v2_fallback: bool = False,
) -> list[OtaInfoRow]:
    """Fetch OTA info through the misc child-facing port."""
    return await self._rest_ports.misc.query_ota_info(
        device_id,
        device_type,
        iot_name=iot_name,
        allow_rich_v2_fallback=allow_rich_v2_fallback,
    )


async def fetch_body_sensor_history(
    self: LiproProtocolFacade,
    device_id: str,
    device_type: int | str,
    sensor_device_id: str,
    mesh_type: str,
) -> JsonObject:
    """Fetch body-sensor history through the misc child-facing port."""
    return await self._rest_ports.misc.fetch_body_sensor_history(
        device_id,
        device_type,
        sensor_device_id,
        mesh_type,
    )


async def fetch_door_sensor_history(
    self: LiproProtocolFacade,
    device_id: str,
    device_type: int | str,
    sensor_device_id: str,
    mesh_type: str,
) -> JsonObject:
    """Fetch door-sensor history through the misc child-facing port."""
    return await self._rest_ports.misc.fetch_door_sensor_history(
        device_id,
        device_type,
        sensor_device_id,
        mesh_type,
    )


async def get_device_schedules(
    self: LiproProtocolFacade,
    device_id: str,
    device_type: int | str,
    *,
    mesh_gateway_id: str = "",
    mesh_member_ids: list[str] | None = None,
) -> list[ScheduleTimingRow]:
    """Fetch device schedules through the schedule child-facing port."""
    return await self._rest_ports.schedule.get_device_schedules(
        device_id,
        device_type,
        mesh_gateway_id=mesh_gateway_id,
        mesh_member_ids=mesh_member_ids,
    )


async def add_device_schedule(
    self: LiproProtocolFacade,
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
    """Add one device schedule through the schedule child-facing port."""
    return await self._rest_ports.schedule.add_device_schedule(
        device_id,
        device_type,
        days,
        times,
        events,
        group_id,
        mesh_gateway_id=mesh_gateway_id,
        mesh_member_ids=mesh_member_ids,
    )


async def delete_device_schedules(
    self: LiproProtocolFacade,
    device_id: str,
    device_type: int | str,
    schedule_ids: list[int],
    group_id: str = "",
    *,
    mesh_gateway_id: str = "",
    mesh_member_ids: list[str] | None = None,
) -> list[ScheduleTimingRow]:
    """Delete device schedules through the schedule child-facing port."""
    return await self._rest_ports.schedule.delete_device_schedules(
        device_id,
        device_type,
        schedule_ids,
        group_id,
        mesh_gateway_id=mesh_gateway_id,
        mesh_member_ids=mesh_member_ids,
    )
