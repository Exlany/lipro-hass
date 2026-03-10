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
        if self.coordinator.mqtt_runtime is None:
            return False
        return self.coordinator.mqtt_runtime.is_connected

    async def async_setup(self) -> bool:
        """Set up coordinator-managed MQTT runtime."""
        return await self.coordinator.async_setup_mqtt()

    async def async_stop(self) -> None:
        """Stop coordinator-managed MQTT runtime."""
        if self.coordinator.mqtt_runtime:
            await self.coordinator.mqtt_runtime.disconnect()

    async def async_sync_subscriptions(self) -> None:
        """Sync subscriptions using the wrapped coordinator state."""
        if self.coordinator.mqtt_client and self.coordinator.biz_id:
            device_ids = [
                device.serial
                for device in self.coordinator.devices.values()
                if device.is_group
            ]
            if device_ids and self.coordinator.mqtt_runtime:
                await self.coordinator.mqtt_runtime.connect(
                    device_ids=device_ids,
                    biz_id=self.coordinator.biz_id,
                )
