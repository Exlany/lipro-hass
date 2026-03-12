"""Coordinator MQTT service - API stability layer.

This service provides a stable facade over the MQTT runtime, implementing
the Stable Interface Pattern from Clean Architecture.

Design rationale:
- **API Stability**: Isolates Entity layer from MqttRuntime implementation changes
- **Dependency Inversion**: Entity depends on Service interface, not Runtime
- **Single Responsibility**: Focused on MQTT connection coordination

Architecture role:
- NOT a business logic layer (logic lives in MqttRuntime)
- NOT a message broker (MqttRuntime handles that)
- IS a stable API boundary (protects Entity layer from Runtime refactoring)

This is intentional "thin proxy" design - the value is in API stability,
not in adding messaging complexity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..mqtt.setup import build_mqtt_subscription_device_ids

if TYPE_CHECKING:
    from ..coordinator import Coordinator


@dataclass(slots=True)
class CoordinatorMqttService:
    """Expose MQTT lifecycle calls through a composition-friendly adapter."""

    coordinator: Coordinator

    @property
    def connected(self) -> bool:
        """Return whether the wrapped coordinator reports MQTT connected."""
        if self.coordinator.mqtt_runtime is None:
            return False
        return self.coordinator.mqtt_runtime.is_connected  # type: ignore[no-any-return]

    async def async_setup(self) -> bool:
        """Set up coordinator-managed MQTT runtime."""
        return await self.coordinator.async_setup_mqtt()

    async def async_stop(self) -> None:
        """Stop coordinator-managed MQTT runtime."""
        if self.coordinator.mqtt_runtime:
            await self.coordinator.mqtt_runtime.disconnect()

    async def async_sync_subscriptions(self) -> None:
        """Sync subscriptions using the wrapped coordinator state."""
        desired_device_ids = build_mqtt_subscription_device_ids(self.coordinator.devices)

        if self.coordinator.mqtt_runtime is None:
            return

        if self.coordinator.mqtt_client is None:
            if desired_device_ids:
                await self.coordinator.async_setup_mqtt()
            return

        await self.coordinator.mqtt_runtime.sync_subscriptions(desired_device_ids)
