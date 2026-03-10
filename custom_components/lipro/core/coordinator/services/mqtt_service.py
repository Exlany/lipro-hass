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
        return self.coordinator._mqtt_runtime._connection_manager.is_connected()

    async def async_setup(self) -> bool:
        """Set up coordinator-managed MQTT runtime."""
        # TODO: Implement MQTT setup via MqttRuntime
        return False

    async def async_stop(self) -> None:
        """Stop coordinator-managed MQTT runtime."""
        # TODO: Implement MQTT stop via MqttRuntime
        pass

    async def async_sync_subscriptions(self) -> None:
        """Sync subscriptions using the wrapped coordinator state."""
        # TODO: Implement subscription sync via MqttRuntime
        pass
