"""Coordinator service protocols used for gradual composition refactoring."""

from __future__ import annotations

from typing import Any, Protocol

from ..device import LiproDevice


class StateManagementProtocol(Protocol):
    """Service contract for coordinator state lookups."""

    @property
    def devices(self) -> dict[str, LiproDevice]:
        """Return the coordinator device map."""

    def get_device(self, serial: str) -> LiproDevice | None:
        """Resolve one device by serial."""

    def get_device_by_id(self, device_id: object) -> LiproDevice | None:
        """Resolve one device by any known identifier."""


class MqttServiceProtocol(Protocol):
    """Service contract for coordinator-managed MQTT lifecycle."""

    @property
    def connected(self) -> bool:
        """Return whether coordinator MQTT runtime is connected."""

    async def async_setup(self) -> bool:
        """Set up MQTT runtime for the current coordinator state."""

    async def async_stop(self) -> None:
        """Stop MQTT runtime for the current coordinator state."""

    async def async_sync_subscriptions(self) -> None:
        """Sync MQTT subscriptions with the current device snapshot."""


class CommandServiceProtocol(Protocol):
    """Service contract for coordinator command dispatch."""

    @property
    def last_failure(self) -> dict[str, Any] | None:
        """Return the latest normalized command failure payload."""

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
        fallback_device_id: str | None = None,
    ) -> bool:
        """Dispatch one device command via the coordinator."""


class DeviceRefreshServiceProtocol(Protocol):
    """Service contract for device lookup and refresh operations."""

    @property
    def devices(self) -> dict[str, LiproDevice]:
        """Return the coordinator device map."""

    def get_device_by_id(self, device_id: object) -> LiproDevice | None:
        """Resolve one device by any known identifier."""

    async def async_refresh_devices(self) -> None:
        """Force-refresh the coordinator device snapshot."""


__all__ = [
    "CommandServiceProtocol",
    "DeviceRefreshServiceProtocol",
    "MqttServiceProtocol",
    "StateManagementProtocol",
]
