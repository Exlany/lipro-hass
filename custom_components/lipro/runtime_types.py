# ruff: noqa: D102
"""Shared runtime coordinator protocols."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from datetime import timedelta
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol

from homeassistant.core import CALLBACK_TYPE, callback

from .core.api.types import JsonObject
from .services.contracts import CommandFailureSummary, ServicePropertyList

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .core.api.types import DiagnosticsApiResponse, OtaInfoRow, ScheduleTimingRow
    from .core.command.result import CommandResultPayload
    from .core.coordinator.entity_protocol import LiproEntityProtocol
    from .core.coordinator.types import RuntimeTelemetrySnapshot
    from .core.device import LiproDevice


type CommandProperties = ServicePropertyList
type ProtocolDiagnosticsSnapshot = JsonObject


class RuntimeReauthReason(StrEnum):
    """Stable reauth reasons exposed across runtime-owned auth surfaces."""

    AUTH_ERROR = "auth_error"
    AUTH_EXPIRED = "auth_expired"


class RuntimeEntityLike(Protocol):
    """Minimal entity surface consumed by coordinator registration helpers."""

    @property
    def entity_id(self) -> str: ...

    @property
    def device(self) -> LiproDevice: ...


class DeviceRefreshServiceLike(Protocol):
    """Stable device-refresh surface exposed by the coordinator."""

    @property
    def devices(self) -> Mapping[str, LiproDevice]: ...

    def get_device_by_id(self, device_id: str) -> LiproDevice | None: ...

    def request_force_refresh(self) -> None: ...

    def request_group_reconciliation(
        self,
        *,
        device_name: str,
        timestamp: float,
    ) -> None: ...

    async def async_refresh_devices(self) -> None: ...


class MqttServiceLike(Protocol):
    """Stable MQTT lifecycle surface exposed by the coordinator."""

    @property
    def connected(self) -> bool: ...

    async def async_setup(self) -> bool: ...

    async def async_stop(self) -> None: ...

    async def async_sync_subscriptions(self) -> None: ...


class CommandServiceLike(Protocol):
    """Stable command-dispatch surface exposed by the coordinator."""

    @property
    def last_failure(self) -> CommandFailureSummary | None: ...

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: CommandProperties | None = None,
        fallback_device_id: str | None = None,
    ) -> bool: ...


class ScheduleMeshDeviceLike(Protocol):
    """Minimal device surface required by schedule-facing runtime services."""

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


class ProtocolServiceLike(Protocol):
    """Stable runtime-owned protocol capability surface for external consumers."""

    async def async_get_device_schedules(
        self,
        device_id: str,
        device_type: str | int,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]: ...

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
    ) -> list[ScheduleTimingRow]: ...

    async def async_delete_device_schedules(
        self,
        device_id: str,
        device_type: str | int,
        schedule_ids: list[int],
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]: ...

    async def async_get_device_schedules_for_device(
        self,
        device: ScheduleMeshDeviceLike,
    ) -> list[ScheduleTimingRow]: ...

    async def async_add_device_schedule_for_device(
        self,
        device: ScheduleMeshDeviceLike,
        days: list[int],
        times: list[int],
        events: list[int],
    ) -> list[ScheduleTimingRow]: ...

    async def async_delete_device_schedules_for_device(
        self,
        device: ScheduleMeshDeviceLike,
        schedule_ids: list[int],
    ) -> list[ScheduleTimingRow]: ...

    async def async_query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: str | int,
    ) -> CommandResultPayload: ...

    async def async_get_city(self) -> JsonObject: ...

    async def async_query_user_cloud(self) -> JsonObject: ...

    async def async_fetch_body_sensor_history(
        self,
        *,
        device_id: str,
        device_type: str | int,
        sensor_device_id: str,
        mesh_type: str,
    ) -> DiagnosticsApiResponse: ...

    async def async_fetch_door_sensor_history(
        self,
        *,
        device_id: str,
        device_type: str | int,
        sensor_device_id: str,
        mesh_type: str,
    ) -> DiagnosticsApiResponse: ...

    async def async_query_ota_info(
        self,
        *,
        device_id: str,
        device_type: str | int,
        iot_name: str | None,
        allow_rich_v2_fallback: bool,
    ) -> list[OtaInfoRow]: ...


class ScheduleServiceLike(Protocol):
    """Stable schedule surface exposed outside the runtime plane."""

    async def async_get_schedules(
        self,
        device: ScheduleMeshDeviceLike,
    ) -> list[ScheduleTimingRow]: ...

    async def async_add_schedule(
        self,
        device: ScheduleMeshDeviceLike,
        days: list[int],
        times: list[int],
        events: list[int],
    ) -> list[ScheduleTimingRow]: ...

    async def async_delete_schedules(
        self,
        device: ScheduleMeshDeviceLike,
        schedule_ids: list[int],
    ) -> list[ScheduleTimingRow]: ...


class RuntimeAuthServiceLike(Protocol):
    """Stable coordinator-auth surface exposed outside the runtime plane."""

    async def async_ensure_authenticated(self) -> None: ...

    async def async_trigger_reauth(self, reason: RuntimeReauthReason) -> None: ...


class ProtocolDiagnosticsContextLike(Protocol):
    """Minimal diagnostics-context surface consumed by telemetry bridges."""

    def snapshot(self, **kwargs: object) -> ProtocolDiagnosticsSnapshot: ...


class ProtocolTelemetryFacadeLike(Protocol):
    """Formal protocol telemetry surface exposed to control-plane bridges."""

    def protocol_diagnostics_snapshot(self) -> ProtocolDiagnosticsSnapshot: ...

    @property
    def diagnostics_context(self) -> ProtocolDiagnosticsContextLike: ...


class RuntimeTelemetryServiceLike(Protocol):
    """Stable runtime telemetry surface consumed by control-plane bridges."""

    def build_snapshot(self) -> RuntimeTelemetrySnapshot: ...


class LiproRuntimeCoordinator(Protocol):
    """Runtime coordinator surface consumed by HA platforms and entities."""

    config_entry: ConfigEntry | None
    last_update_success: bool

    @property
    def devices(self) -> Mapping[str, LiproDevice]: ...

    def iter_devices(self) -> Iterable[LiproDevice]: ...

    async def async_request_refresh(self) -> None: ...

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: CommandProperties | None = None,
    ) -> bool: ...

    async def async_apply_optimistic_state(
        self,
        device: LiproDevice,
        properties: JsonObject,
    ) -> None: ...

    async def async_query_device_ota_info(
        self,
        device: LiproDevice,
        *,
        allow_rich_v2_fallback: bool | None = None,
    ) -> list[OtaInfoRow]: ...

    def get_device(self, device_id: str) -> LiproDevice | None: ...

    def get_device_by_id(self, device_id: str) -> LiproDevice | None: ...

    def register_entity(self, entity: LiproEntityProtocol) -> None: ...

    def unregister_entity(self, entity: LiproEntityProtocol) -> None: ...

    def async_update_listeners(self) -> None: ...


class LiproCoordinator(LiproRuntimeCoordinator, Protocol):
    """Formal runtime public surface consumed outside the coordinator plane."""

    update_interval: timedelta | None

    @property
    def auth_service(self) -> RuntimeAuthServiceLike: ...

    @property
    def device_refresh_service(self) -> DeviceRefreshServiceLike: ...

    @property
    def schedule_service(self) -> ScheduleServiceLike: ...

    @property
    def mqtt_service(self) -> MqttServiceLike: ...

    @property
    def command_service(self) -> CommandServiceLike: ...

    @property
    def protocol(self) -> ProtocolTelemetryFacadeLike: ...

    @property
    def protocol_service(self) -> ProtocolServiceLike: ...

    @property
    def telemetry_service(self) -> RuntimeTelemetryServiceLike: ...

    @callback
    def async_add_listener(
        self,
        update_callback: CALLBACK_TYPE,
        context: object | None = None,
    ) -> Callable[[], None]: ...


__all__ = [
    "CommandServiceLike",
    "DeviceRefreshServiceLike",
    "LiproCoordinator",
    "LiproRuntimeCoordinator",
    "MqttServiceLike",
    "ProtocolDiagnosticsContextLike",
    "ProtocolServiceLike",
    "ProtocolTelemetryFacadeLike",
    "RuntimeAuthServiceLike",
    "RuntimeEntityLike",
    "RuntimeReauthReason",
    "RuntimeTelemetryServiceLike",
    "ScheduleMeshDeviceLike",
]
