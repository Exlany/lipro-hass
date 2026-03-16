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

    from .core.api.types import OtaInfoRow
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


class LiproCoordinator(Protocol):
    """Narrow public runtime surface consumed outside the coordinator plane."""

    config_entry: ConfigEntry | None
    last_update_success: bool
    update_interval: timedelta | None

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
    "RuntimeEntityLike",
]
