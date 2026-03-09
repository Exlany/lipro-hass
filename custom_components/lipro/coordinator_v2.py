"""Composable coordinator facade built on service protocols."""

from __future__ import annotations

from typing import Any

from .core.coordinator import LiproDataUpdateCoordinator
from .core.coordinator.protocols import (
    CommandServiceProtocol,
    DeviceRefreshServiceProtocol,
    MqttServiceProtocol,
    StateManagementProtocol,
)
from .core.device import LiproDevice


class CoordinatorV2:
    """New coordinator facade composed from explicit services."""

    def __init__(
        self,
        *,
        state_service: StateManagementProtocol,
        command_service: CommandServiceProtocol,
        device_refresh_service: DeviceRefreshServiceProtocol,
        mqtt_service: MqttServiceProtocol,
        delegate: Any | None = None,
    ) -> None:
        """Initialize the composed coordinator facade."""
        self.state_service = state_service
        self.command_service = command_service
        self.device_refresh_service = device_refresh_service
        self.mqtt_service = mqtt_service
        self._delegate = delegate

    @classmethod
    def from_legacy(cls, coordinator: LiproDataUpdateCoordinator) -> CoordinatorV2:
        """Build a composed facade from the current coordinator instance."""
        return cls(
            state_service=coordinator.state_service,
            command_service=coordinator.command_service,
            device_refresh_service=coordinator.device_refresh_service,
            mqtt_service=coordinator.mqtt_service,
            delegate=coordinator,
        )

    @property
    def devices(self) -> dict[str, LiproDevice]:
        """Return all known devices."""
        return self.state_service.devices

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

    def __getattr__(self, name: str) -> Any:
        """Fallback to the wrapped legacy coordinator during migration."""
        if self._delegate is None:
            msg = f"{type(self).__name__!s} has no attribute {name!r}"
            raise AttributeError(msg)
        return getattr(self._delegate, name)


__all__ = ["CoordinatorV2"]
