"""Typed REST child-façade port for the unified protocol root."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Protocol

from ..api.auth_recovery import AuthRecoveryTelemetrySnapshot
from ..api.types import (
    DeviceListResponse,
    JsonObject,
    LoginResponse,
    OtaInfoRow,
    ScheduleTimingRow,
)
from .contracts import (
    CanonicalDeviceStatusRow,
    CanonicalMeshGroupStatusRow,
    CanonicalMqttConfig,
    OutletPowerInfoResult,
)

type StatusBatchMetric = Callable[[int, float, int], None]
type TokenRefreshCallback = Callable[[], Awaitable[None]]


class _RestFacadePort(Protocol):
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
    async def get_devices(self, offset: int = 0, limit: int = 100) -> DeviceListResponse: ...
    async def get_product_configs(self) -> list[JsonObject]: ...
    async def query_device_status(
        self,
        device_ids: list[str],
        *,
        max_devices_per_query: int = 100,
        on_batch_metric: StatusBatchMetric | None = None,
    ) -> list[CanonicalDeviceStatusRow]: ...
    async def query_mesh_group_status(
        self,
        group_ids: list[str],
    ) -> list[CanonicalMeshGroupStatusRow]: ...
    async def query_connect_status(self, device_ids: list[str]) -> dict[str, bool]: ...
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
    async def get_mqtt_config(self) -> CanonicalMqttConfig: ...
    async def fetch_outlet_power_info(self, device_id: str) -> OutletPowerInfoResult: ...
    async def query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: int | str,
    ) -> JsonObject: ...
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

    def auth_recovery_telemetry_snapshot(self) -> AuthRecoveryTelemetrySnapshot: ...


__all__ = ["StatusBatchMetric", "TokenRefreshCallback", "_RestFacadePort"]
