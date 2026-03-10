"""Coordinator MQTT service boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..coordinator import Coordinator


@dataclass(slots=True)
class CoordinatorMqttService:
    """Expose MQTT lifecycle calls through a composition-friendly adapter."""

    coordinator: Coordinator

    @property
    def connected(self) -> bool:
        """Return whether the wrapped coordinator reports MQTT connected."""
        return self.coordinator.mqtt_connected

    async def async_setup(self) -> bool:
        """Set up coordinator-managed MQTT runtime."""
        return await self.coordinator.async_setup_mqtt_runtime()

    async def async_stop(self) -> None:
        """Stop coordinator-managed MQTT runtime."""
        await self.coordinator.async_stop_mqtt_runtime()

    async def async_sync_subscriptions(self) -> None:
        """Sync subscriptions using the wrapped coordinator state."""
        await self.coordinator.async_sync_mqtt_subscriptions_runtime()
