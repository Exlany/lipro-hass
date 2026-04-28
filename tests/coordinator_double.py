"""Coordinator test double moved out of ``tests.conftest`` to keep fixtures thin."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from datetime import timedelta
from types import MappingProxyType
from typing import TYPE_CHECKING, Any
from unittest.mock import DEFAULT, AsyncMock, MagicMock

if TYPE_CHECKING:
    from custom_components.lipro.core.device import LiproDevice


class _CoordinatorDouble:
    """Coordinator test double aligned with the formal runtime surface."""

    def __init__(self) -> None:
        self._devices_store: dict[str, Any] = {}
        self._devices_view = MappingProxyType(self._devices_store)
        self._device_locks: dict[str, asyncio.Lock] = {}
        self.config_entry: Any | None = None
        self.update_interval: timedelta | None = None
        self.last_update_success = True
        self.async_send_command: Any = AsyncMock(return_value=True)
        self.async_request_refresh: Any = AsyncMock()
        self.async_update_listeners: Any = MagicMock()
        self.register_entity: Any = MagicMock()
        self.unregister_entity: Any = MagicMock()
        self.async_add_listener: Any = MagicMock(return_value=lambda: None)

        async def _async_command_service_send_command(
            device: Any,
            command: str,
            properties: list[dict[str, str]] | None = None,
        ) -> Any:
            return await self.async_send_command(device, command, properties)

        self.command_service: Any = MagicMock(last_failure=None)
        self.command_service.async_send_command = AsyncMock(
            side_effect=_async_command_service_send_command
        )

        self.get_device: Any = MagicMock()
        self.get_device.side_effect = self._lookup_get_device
        self.get_device_by_id: Any = MagicMock()
        self.get_device_by_id.side_effect = self._lookup_get_device_by_id
        self.get_device_lock: Any = MagicMock(side_effect=self._get_device_lock)

        async def _async_apply_optimistic_state(
            device: Any,
            properties: Mapping[str, object],
        ) -> None:
            device_lock = self._get_device_lock(device.serial)
            async with device_lock:
                device.update_properties(dict(properties))

        self.async_apply_optimistic_state: Any = AsyncMock(
            side_effect=_async_apply_optimistic_state
        )

        self.auth_service: Any = MagicMock(
            async_ensure_authenticated=AsyncMock(),
            async_trigger_reauth=AsyncMock(),
        )

        self.protocol: Any = MagicMock()
        self.protocol.query_ota_info = AsyncMock(return_value=[])
        self.protocol.get_device_schedules = AsyncMock(return_value=[])
        self.protocol.add_device_schedule = AsyncMock(return_value=[])
        self.protocol.delete_device_schedules = AsyncMock(return_value=[])
        self.protocol.query_command_result = AsyncMock(return_value={})
        self.protocol.get_city = AsyncMock(return_value={})
        self.protocol.query_user_cloud = AsyncMock(return_value={})
        self.protocol.fetch_body_sensor_history = AsyncMock(return_value={})
        self.protocol.fetch_door_sensor_history = AsyncMock(return_value={})
        self.protocol.protocol_diagnostics_snapshot = MagicMock(return_value={})
        self.protocol.diagnostics_context = MagicMock(
            snapshot=MagicMock(return_value={})
        )

        async def _async_query_ota_info(**kwargs: Any) -> Any:
            return await self.protocol.query_ota_info(**kwargs)

        async def _async_get_device_schedules(*args: Any, **kwargs: Any) -> Any:
            return await self.protocol.get_device_schedules(*args, **kwargs)

        async def _async_add_device_schedule(*args: Any, **kwargs: Any) -> Any:
            return await self.protocol.add_device_schedule(*args, **kwargs)

        async def _async_delete_device_schedules(*args: Any, **kwargs: Any) -> Any:
            return await self.protocol.delete_device_schedules(*args, **kwargs)

        async def _async_query_command_result(**kwargs: Any) -> Any:
            return await self.protocol.query_command_result(**kwargs)

        async def _async_get_city() -> Any:
            return await self.protocol.get_city()

        async def _async_query_user_cloud() -> Any:
            return await self.protocol.query_user_cloud()

        async def _async_fetch_body_sensor_history(**kwargs: Any) -> Any:
            return await self.protocol.fetch_body_sensor_history(**kwargs)

        async def _async_fetch_door_sensor_history(**kwargs: Any) -> Any:
            return await self.protocol.fetch_door_sensor_history(**kwargs)

        self.async_query_ota_info = AsyncMock(side_effect=_async_query_ota_info)

        async def _async_query_device_ota_info(
            device: Any,
            *,
            allow_rich_v2_fallback: bool | None = None,
        ) -> Any:
            return await self.protocol.query_ota_info(
                device_id=device.serial,
                device_type=device.device_type_hex,
                iot_name=device.iot_name or None,
                allow_rich_v2_fallback=(
                    device.capabilities.is_light
                    if allow_rich_v2_fallback is None
                    else allow_rich_v2_fallback
                ),
            )

        self.async_query_device_ota_info = AsyncMock(
            side_effect=_async_query_device_ota_info
        )
        self.async_query_command_result = AsyncMock(
            side_effect=_async_query_command_result
        )
        self.async_get_city = AsyncMock(side_effect=_async_get_city)
        self.async_query_user_cloud = AsyncMock(side_effect=_async_query_user_cloud)
        self.async_fetch_body_sensor_history = AsyncMock(
            side_effect=_async_fetch_body_sensor_history
        )
        self.async_fetch_door_sensor_history = AsyncMock(
            side_effect=_async_fetch_door_sensor_history
        )

        self.protocol_service: Any = MagicMock()
        self.protocol_service.async_get_device_schedules = AsyncMock(
            side_effect=_async_get_device_schedules
        )
        self.protocol_service.async_add_device_schedule = AsyncMock(
            side_effect=_async_add_device_schedule
        )
        self.protocol_service.async_delete_device_schedules = AsyncMock(
            side_effect=_async_delete_device_schedules
        )
        self.protocol_service.async_get_device_schedules_for_device = AsyncMock(
            side_effect=_async_get_device_schedules
        )
        self.protocol_service.async_add_device_schedule_for_device = AsyncMock(
            side_effect=_async_add_device_schedule
        )
        self.protocol_service.async_delete_device_schedules_for_device = AsyncMock(
            side_effect=_async_delete_device_schedules
        )
        self.protocol_service.async_query_ota_info = AsyncMock(
            side_effect=_async_query_ota_info
        )
        self.protocol_service.async_query_command_result = AsyncMock(
            side_effect=_async_query_command_result
        )
        self.protocol_service.async_get_city = AsyncMock(side_effect=_async_get_city)
        self.protocol_service.async_query_user_cloud = AsyncMock(
            side_effect=_async_query_user_cloud
        )
        self.protocol_service.async_fetch_body_sensor_history = AsyncMock(
            side_effect=_async_fetch_body_sensor_history
        )
        self.protocol_service.async_fetch_door_sensor_history = AsyncMock(
            side_effect=_async_fetch_door_sensor_history
        )

        self.schedule_service = MagicMock(
            async_get_schedules=self.protocol_service.async_get_device_schedules_for_device,
            async_add_schedule=self.protocol_service.async_add_device_schedule_for_device,
            async_delete_schedules=self.protocol_service.async_delete_device_schedules_for_device,
        )

        self.device_refresh_service: Any = MagicMock()
        self.device_refresh_service.devices = self.devices
        self.device_refresh_service.get_device_by_id = self.get_device_by_id
        self.device_refresh_service.request_force_refresh = MagicMock()
        self.device_refresh_service.request_group_reconciliation = MagicMock()
        self.device_refresh_service.async_refresh_devices = AsyncMock()

        self.mqtt_service: Any = MagicMock(connected=True)
        self.mqtt_service.async_setup = AsyncMock(return_value=True)
        self.mqtt_service.async_stop = AsyncMock()
        self.mqtt_service.async_sync_subscriptions = AsyncMock()

        self.telemetry_service: Any = MagicMock()
        self.telemetry_service.build_snapshot = MagicMock(return_value={})

    @property
    def devices(self) -> Mapping[str, Any]:
        return self._devices_view

    @devices.setter
    def devices(self, value: Mapping[str, Any]) -> None:
        self._devices_store = dict(value)
        self._devices_view = MappingProxyType(self._devices_store)
        self.device_refresh_service.devices = self._devices_view

    def iter_devices(self) -> tuple[LiproDevice, ...]:
        return tuple(self._devices_view.values())

    def _lookup_get_device(self, serial: str) -> Any:
        if self.get_device._mock_return_value is not DEFAULT:
            return self.get_device._mock_return_value
        return self._devices_store.get(serial)

    def _lookup_get_device_by_id(self, device_id: str) -> Any:
        if self.get_device_by_id._mock_return_value is not DEFAULT:
            return self.get_device_by_id._mock_return_value
        return self._devices_store.get(device_id)

    def _get_device_lock(self, serial: str) -> asyncio.Lock:
        return self._device_locks.setdefault(serial, asyncio.Lock())

    def set_device(self, device: Any) -> None:
        self._devices_store[device.serial] = device
        self.device_refresh_service.devices = self._devices_view

    def set_devices(self, *devices: Any) -> None:
        self.devices = {device.serial: device for device in devices}


__all__ = ["_CoordinatorDouble"]
