# ruff: noqa: D102
"""Shared runtime coordinator protocols."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping
from datetime import timedelta
from typing import TYPE_CHECKING, Protocol

from homeassistant.core import CALLBACK_TYPE, callback

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .core.api.types import DiagnosticsApiResponse, OtaInfoRow
    from .core.command.result import CommandResultPayload
    from .core.device import LiproDevice


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

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
    ) -> bool: ...


class RuntimeAuthServiceLike(Protocol):
    """Stable coordinator-auth surface exposed outside the runtime plane."""

    async def async_ensure_authenticated(self) -> None: ...

    async def async_trigger_reauth(self, reason: str) -> None: ...


class LiproCoordinator(Protocol):
    """Formal runtime public surface consumed outside the coordinator plane."""

    config_entry: ConfigEntry | None
    last_update_success: bool
    update_interval: timedelta | None

    @property
    def auth_service(self) -> RuntimeAuthServiceLike: ...

    @property
    def device_refresh_service(self) -> DeviceRefreshServiceLike: ...

    @property
    def mqtt_service(self) -> MqttServiceLike: ...

    @property
    def command_service(self) -> CommandServiceLike: ...

    @property
    def devices(self) -> Mapping[str, LiproDevice]: ...

    @callback
    def async_add_listener(
        self,
        update_callback: CALLBACK_TYPE,
        context: object | None = None,
    ) -> Callable[[], None]: ...

    async def async_request_refresh(self) -> None: ...

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
    ) -> bool: ...

    async def async_query_ota_info(
        self,
        *,
        device_id: str,
        device_type: str | int,
        iot_name: str | None,
        allow_rich_v2_fallback: bool,
    ) -> list[OtaInfoRow]: ...

    async def async_query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: str | int,
    ) -> CommandResultPayload: ...

    async def async_get_city(self) -> dict[str, object]: ...

    async def async_query_user_cloud(self) -> dict[str, object]: ...

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

    def get_device(self, device_id: str) -> LiproDevice | None: ...

    def get_device_by_id(self, device_id: str) -> LiproDevice | None: ...

    def get_device_lock(self, device_id: str) -> asyncio.Lock: ...

    def register_entity(self, entity: RuntimeEntityLike) -> None: ...

    def unregister_entity(self, entity: RuntimeEntityLike) -> None: ...

    def async_update_listeners(self) -> None: ...


__all__ = [
    "CommandServiceLike",
    "DeviceRefreshServiceLike",
    "LiproCoordinator",
    "MqttServiceLike",
    "RuntimeAuthServiceLike",
    "RuntimeEntityLike",
]
