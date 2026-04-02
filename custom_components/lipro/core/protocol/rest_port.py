"""Concern-local REST child-facing ports for the unified protocol root."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from ..api.auth_recovery import AuthRecoveryTelemetrySnapshot
from ..api.types import (
    CommandResultApiResponse,
    DeviceListResponse,
    DeviceStatusItem,
    JsonObject,
    LoginResponse,
    MqttConfigResponse,
    OtaInfoRow,
    ScheduleTimingRow,
)
from .contracts import OutletPowerInfoResult

if TYPE_CHECKING:
    from ..api.rest_facade import LiproRestFacade

type StatusBatchMetric = Callable[[int, float, int], None]
type TokenRefreshCallback = Callable[[], Awaitable[None]]


class _RestAuthPort(Protocol):
    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        user_id: int | None = None,
        biz_id: str | None = None,
    ) -> None: ...

    def set_token_refresh_callback(self, callback: TokenRefreshCallback) -> None: ...

    async def login(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> LoginResponse: ...

    async def refresh_access_token(self) -> LoginResponse: ...


class _RestInventoryPort(Protocol):
    async def get_devices(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> DeviceListResponse: ...

    async def get_product_configs(self) -> list[JsonObject]: ...


class _RestStatusPort(Protocol):
    async def query_device_status(
        self,
        device_ids: list[str],
        *,
        max_devices_per_query: int = 100,
        on_batch_metric: StatusBatchMetric | None = None,
    ) -> list[DeviceStatusItem]: ...

    async def query_mesh_group_status(
        self,
        group_ids: list[str],
    ) -> list[JsonObject]: ...

    async def query_connect_status(self, device_ids: list[str]) -> dict[str, bool]: ...


class _RestCommandPort(Protocol):
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

    async def fetch_outlet_power_info(self, device_id: str) -> OutletPowerInfoResult: ...

    async def query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: int | str,
    ) -> CommandResultApiResponse: ...


class _RestMiscPort(Protocol):
    async def get_mqtt_config(self) -> MqttConfigResponse: ...

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


class _RestSchedulePort(Protocol):
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


class _RestDiagnosticsPort(Protocol):
    def auth_recovery_telemetry_snapshot(self) -> AuthRecoveryTelemetrySnapshot: ...


@dataclass
class _BoundRestAuthPort:
    """Explicit auth adapter bound to the REST child façade."""

    rest_facade: LiproRestFacade

    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        user_id: int | None = None,
        biz_id: str | None = None,
    ) -> None:
        self.rest_facade.set_tokens(
            access_token,
            refresh_token,
            user_id=user_id,
            biz_id=biz_id,
        )

    def set_token_refresh_callback(self, callback: TokenRefreshCallback) -> None:
        self.rest_facade.set_token_refresh_callback(callback)

    async def login(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> LoginResponse:
        return await self.rest_facade.login(
            phone,
            password,
            password_is_hashed=password_is_hashed,
        )

    async def refresh_access_token(self) -> LoginResponse:
        return await self.rest_facade.refresh_access_token()


@dataclass
class _BoundRestInventoryPort:
    """Explicit inventory adapter bound to the REST child façade."""

    rest_facade: LiproRestFacade

    async def get_devices(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> DeviceListResponse:
        return await self.rest_facade.get_devices(offset=offset, limit=limit)

    async def get_product_configs(self) -> list[JsonObject]:
        return await self.rest_facade.get_product_configs()


@dataclass
class _BoundRestStatusPort:
    """Explicit status adapter bound to the REST child façade."""

    rest_facade: LiproRestFacade

    async def query_device_status(
        self,
        device_ids: list[str],
        *,
        max_devices_per_query: int = 100,
        on_batch_metric: StatusBatchMetric | None = None,
    ) -> list[DeviceStatusItem]:
        return await self.rest_facade.query_device_status(
            device_ids,
            max_devices_per_query=max_devices_per_query,
            on_batch_metric=on_batch_metric,
        )

    async def query_mesh_group_status(
        self,
        group_ids: list[str],
    ) -> list[JsonObject]:
        return await self.rest_facade.query_mesh_group_status(group_ids)

    async def query_connect_status(self, device_ids: list[str]) -> dict[str, bool]:
        return await self.rest_facade.query_connect_status(device_ids)


@dataclass
class _BoundRestCommandPort:
    """Explicit command adapter bound to the REST child façade."""

    rest_facade: LiproRestFacade

    async def send_command(
        self,
        device_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> JsonObject:
        return await self.rest_facade.send_command(
            device_id,
            command,
            device_type,
            properties,
            iot_name,
        )

    async def send_group_command(
        self,
        group_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> JsonObject:
        return await self.rest_facade.send_group_command(
            group_id,
            command,
            device_type,
            properties,
            iot_name,
        )

    async def fetch_outlet_power_info(self, device_id: str) -> OutletPowerInfoResult:
        return await self.rest_facade.fetch_outlet_power_info(device_id)

    async def query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: int | str,
    ) -> CommandResultApiResponse:
        return await self.rest_facade.query_command_result(
            msg_sn=msg_sn,
            device_id=device_id,
            device_type=device_type,
        )


@dataclass
class _BoundRestMiscPort:
    """Explicit misc/diagnostics adapter bound to the REST child façade."""

    rest_facade: LiproRestFacade

    async def get_mqtt_config(self) -> MqttConfigResponse:
        return await self.rest_facade.get_mqtt_config()

    async def get_city(self) -> JsonObject:
        return await self.rest_facade.get_city()

    async def query_user_cloud(self) -> JsonObject:
        return await self.rest_facade.query_user_cloud()

    async def query_ota_info(
        self,
        device_id: str,
        device_type: int | str,
        *,
        iot_name: str | None = None,
        allow_rich_v2_fallback: bool = False,
    ) -> list[OtaInfoRow]:
        return await self.rest_facade.query_ota_info(
            device_id,
            device_type,
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
        return await self.rest_facade.fetch_body_sensor_history(
            device_id,
            device_type,
            sensor_device_id,
            mesh_type,
        )

    async def fetch_door_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> JsonObject:
        return await self.rest_facade.fetch_door_sensor_history(
            device_id,
            device_type,
            sensor_device_id,
            mesh_type,
        )


@dataclass
class _BoundRestSchedulePort:
    """Explicit schedule adapter bound to the REST child façade."""

    rest_facade: LiproRestFacade

    async def get_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        return await self.rest_facade.get_device_schedules(
            device_id,
            device_type,
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
        return await self.rest_facade.add_device_schedule(
            device_id,
            device_type,
            days,
            times,
            events,
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
        return await self.rest_facade.delete_device_schedules(
            device_id,
            device_type,
            schedule_ids,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )


@dataclass
class _BoundRestDiagnosticsPort:
    """Explicit diagnostics adapter bound to the REST child façade."""

    rest_facade: LiproRestFacade

    def auth_recovery_telemetry_snapshot(self) -> AuthRecoveryTelemetrySnapshot:
        return self.rest_facade.auth_recovery_telemetry_snapshot()


@dataclass(frozen=True, slots=True)
class ProtocolRestPortFamily:
    """Concern-local REST child-facing contracts used by the protocol root."""

    auth: _RestAuthPort
    inventory: _RestInventoryPort
    status: _RestStatusPort
    command: _RestCommandPort
    misc: _RestMiscPort
    schedule: _RestSchedulePort
    diagnostics: _RestDiagnosticsPort


def bind_protocol_rest_port_family(rest_facade: LiproRestFacade) -> ProtocolRestPortFamily:
    """Bind the canonical REST child façade into concern-local child-facing ports."""
    return ProtocolRestPortFamily(
        auth=_BoundRestAuthPort(rest_facade),
        inventory=_BoundRestInventoryPort(rest_facade),
        status=_BoundRestStatusPort(rest_facade),
        command=_BoundRestCommandPort(rest_facade),
        misc=_BoundRestMiscPort(rest_facade),
        schedule=_BoundRestSchedulePort(rest_facade),
        diagnostics=_BoundRestDiagnosticsPort(rest_facade),
    )


__all__ = [
    "ProtocolRestPortFamily",
    "StatusBatchMetric",
    "TokenRefreshCallback",
    "bind_protocol_rest_port_family",
]
