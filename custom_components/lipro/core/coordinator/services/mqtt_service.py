"""Coordinator MQTT service - stable MQTT lifecycle surface."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..mqtt.setup import build_mqtt_subscription_device_ids

if TYPE_CHECKING:
    from ...device import LiproDevice
    from ..runtime.mqtt_runtime import MqttRuntime


@dataclass(slots=True)
class CoordinatorMqttService:
    """Expose MQTT lifecycle calls without leaking runtime internals."""

    devices_getter: Callable[[], dict[str, LiproDevice]]
    mqtt_runtime_getter: Callable[[], MqttRuntime]
    setup_callback: Callable[[], Awaitable[bool]]

    @property
    def connected(self) -> bool:
        """Return whether the coordinator-managed MQTT runtime is connected."""
        return self.mqtt_runtime_getter().is_connected

    async def async_setup(self) -> bool:
        """Set up coordinator-managed MQTT runtime."""
        return await self.setup_callback()

    async def async_stop(self) -> None:
        """Stop coordinator-managed MQTT runtime."""
        await self.mqtt_runtime_getter().disconnect()

    async def async_sync_subscriptions(self) -> None:
        """Sync MQTT subscriptions from the canonical device map."""
        desired_device_ids = build_mqtt_subscription_device_ids(self.devices_getter())
        if not desired_device_ids:
            return

        mqtt_runtime = self.mqtt_runtime_getter()
        if not mqtt_runtime.has_transport:
            await self.setup_callback()
            return

        await mqtt_runtime.sync_subscriptions(desired_device_ids)
