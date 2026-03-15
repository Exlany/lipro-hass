# ruff: noqa: D102
"""Shared runtime coordinator protocols."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any, Protocol

from homeassistant.core import CALLBACK_TYPE, callback

if TYPE_CHECKING:
    from .core.api.types import OtaInfoRow
    from .core.device import LiproDevice


class LiproCoordinator(Protocol):
    """Narrow public runtime surface consumed outside the coordinator plane."""

    config_entry: Any | None
    last_update_success: bool
    update_interval: Any
    device_refresh_service: Any
    mqtt_service: Any

    @property
    def devices(self) -> Mapping[str, LiproDevice]: ...


    @callback
    def async_add_listener(
        self, update_callback: CALLBACK_TYPE, context: Any = None
    ) -> Callable[[], None]: ...

    async def async_request_refresh(self) -> None: ...

    async def async_send_command(self, *args: Any, **kwargs: Any) -> bool: ...

    async def async_query_ota_info(self, *args: Any, **kwargs: Any) -> list[OtaInfoRow]: ...

    def get_device(self, device_id: str) -> LiproDevice | None: ...

    def get_device_by_id(self, device_id: str) -> LiproDevice | None: ...

    def get_device_lock(self, device_id: str) -> Any: ...

    def register_entity(self, entity: Any) -> None: ...

    def unregister_entity(self, entity: Any) -> None: ...

    def async_update_listeners(self) -> None: ...


__all__ = ["LiproCoordinator"]
