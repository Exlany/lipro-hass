"""Composable coordinator facade built on explicit service boundaries."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from .core.coordinator.protocols import (
    CommandServiceProtocol,
    DeviceRefreshServiceProtocol,
    MqttServiceProtocol,
    StateManagementProtocol,
)
from .core.device import LiproDevice

if TYPE_CHECKING:
    from .core.api.client import LiproClient
    from .core.coordinator import LiproDataUpdateCoordinator
    from .core.coordinator.entity_protocol import LiproEntityProtocol


type AsyncHook = Callable[[], Awaitable[None]]
type BoolGetter = Callable[[], bool]
type EntityHook = Callable[[LiproEntityProtocol], None]
type ReportBuilder = Callable[[], dict[str, Any]]
type SyncHook = Callable[[], None]


class CoordinatorV2:
    """Coordinator facade composed from explicit services and runtime hooks."""

    def __init__(
        self,
        *,
        state_service: StateManagementProtocol,
        command_service: CommandServiceProtocol,
        device_refresh_service: DeviceRefreshServiceProtocol,
        mqtt_service: MqttServiceProtocol,
        client: LiproClient | None = None,
        update_interval: timedelta | None = None,
        last_update_success_getter: BoolGetter | None = None,
        request_refresh: AsyncHook | None = None,
        config_entry_first_refresh: AsyncHook | None = None,
        shutdown: AsyncHook | None = None,
        update_listeners: SyncHook | None = None,
        register_entity: EntityHook | None = None,
        unregister_entity: EntityHook | None = None,
        developer_report_builder: ReportBuilder | None = None,
    ) -> None:
        """Initialize the composed coordinator facade."""
        self.state_service = state_service
        self.command_service = command_service
        self.device_refresh_service = device_refresh_service
        self.mqtt_service = mqtt_service
        self._client = client
        self._update_interval = update_interval
        self._last_update_success_getter = last_update_success_getter
        self._request_refresh = request_refresh
        self._config_entry_first_refresh = config_entry_first_refresh
        self._shutdown = shutdown
        self._update_listeners = update_listeners
        self._register_entity = register_entity
        self._unregister_entity = unregister_entity
        self._developer_report_builder = developer_report_builder

    @classmethod
    def from_legacy(cls, coordinator: LiproDataUpdateCoordinator) -> CoordinatorV2:
        """Build a composed facade from the current coordinator runtime."""
        return cls(
            state_service=coordinator.state_service,
            command_service=coordinator.command_service,
            device_refresh_service=coordinator.device_refresh_service,
            mqtt_service=coordinator.mqtt_service,
            client=coordinator.client,
            update_interval=coordinator.update_interval,
            last_update_success_getter=lambda: coordinator.last_update_success,
            request_refresh=coordinator.async_request_refresh,
            config_entry_first_refresh=coordinator.async_config_entry_first_refresh,
            shutdown=coordinator.async_shutdown,
            update_listeners=coordinator.async_update_listeners,
            register_entity=coordinator.register_entity,
            unregister_entity=coordinator.unregister_entity,
            developer_report_builder=coordinator.build_developer_report,
        )

    @staticmethod
    def _require_async_hook(name: str, hook: AsyncHook | None) -> AsyncHook:
        """Return one required async hook or raise a clear error."""
        if hook is None:
            msg = f"CoordinatorV2 hook is unavailable for {name}()"
            raise AttributeError(msg)
        return hook

    @staticmethod
    def _require_sync_hook(name: str, hook: SyncHook | None) -> SyncHook:
        """Return one required sync hook or raise a clear error."""
        if hook is None:
            msg = f"CoordinatorV2 hook is unavailable for {name}()"
            raise AttributeError(msg)
        return hook

    @staticmethod
    def _require_entity_hook(name: str, hook: EntityHook | None) -> EntityHook:
        """Return one required entity hook or raise a clear error."""
        if hook is None:
            msg = f"CoordinatorV2 hook is unavailable for {name}()"
            raise AttributeError(msg)
        return hook

    @property
    def devices(self) -> dict[str, LiproDevice]:
        """Return all known devices."""
        return self.state_service.devices

    @property
    def mqtt_connected(self) -> bool:
        """Return whether MQTT transport is currently connected."""
        return self.mqtt_service.connected

    @property
    def last_command_failure(self) -> dict[str, Any] | None:
        """Return the latest normalized command failure payload."""
        return self.command_service.last_failure

    @property
    def client(self) -> LiproClient:
        """Return the API client used by the current coordinator runtime."""
        if self._client is None:
            msg = "CoordinatorV2 client is unavailable for this operation"
            raise AttributeError(msg)
        return self._client

    @property
    def update_interval(self) -> timedelta | None:
        """Return the current polling interval."""
        return self._update_interval

    @property
    def last_update_success(self) -> bool:
        """Return the latest refresh status."""
        if self._last_update_success_getter is None:
            msg = "CoordinatorV2 refresh status is unavailable for this operation"
            raise AttributeError(msg)
        return self._last_update_success_getter()

    def get_device(self, serial: str) -> LiproDevice | None:
        """Resolve one device by serial."""
        return self.state_service.get_device(serial)

    def get_device_by_id(self, device_id: object) -> LiproDevice | None:
        """Resolve one device by any known identifier."""
        return self.state_service.get_device_by_id(device_id)

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
        fallback_device_id: str | None = None,
    ) -> bool:
        """Dispatch one device command."""
        return await self.command_service.async_send_command(
            device,
            command,
            properties,
            fallback_device_id,
        )

    async def async_refresh_devices(self) -> None:
        """Trigger a device refresh through the refresh service."""
        await self.device_refresh_service.async_refresh_devices()

    async def async_setup_mqtt(self) -> bool:
        """Set up MQTT through the MQTT service."""
        return await self.mqtt_service.async_setup()

    async def async_stop_mqtt(self) -> None:
        """Stop MQTT through the MQTT service."""
        await self.mqtt_service.async_stop()

    async def async_sync_mqtt_subscriptions(self) -> None:
        """Sync MQTT subscriptions through the MQTT service."""
        await self.mqtt_service.async_sync_subscriptions()

    async def async_request_refresh(self) -> None:
        """Request one refresh cycle from the runtime hooks."""
        await self._require_async_hook(
            "async_request_refresh",
            self._request_refresh,
        )()

    async def async_config_entry_first_refresh(self) -> None:
        """Run the first refresh path from the runtime hooks."""
        await self._require_async_hook(
            "async_config_entry_first_refresh",
            self._config_entry_first_refresh,
        )()

    async def async_shutdown(self) -> None:
        """Shut down the coordinator runtime."""
        await self._require_async_hook("async_shutdown", self._shutdown)()

    def async_update_listeners(self) -> None:
        """Notify listeners through the injected runtime hook."""
        self._require_sync_hook("async_update_listeners", self._update_listeners)()

    def register_entity(self, entity: LiproEntityProtocol) -> None:
        """Register one entity for coordinator-side bookkeeping."""
        self._require_entity_hook("register_entity", self._register_entity)(entity)

    def unregister_entity(self, entity: LiproEntityProtocol) -> None:
        """Unregister one entity from coordinator-side bookkeeping."""
        self._require_entity_hook("unregister_entity", self._unregister_entity)(entity)

    def build_developer_report(self) -> dict[str, Any]:
        """Build one developer report using the injected runtime hook."""
        if self._developer_report_builder is None:
            msg = "CoordinatorV2 developer report is unavailable for this operation"
            raise AttributeError(msg)
        return self._developer_report_builder()


__all__ = ["CoordinatorV2"]
