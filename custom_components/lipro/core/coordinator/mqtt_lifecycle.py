"""MQTT lifecycle management for coordinator (Phase H2).

This module extracts MQTT setup/teardown logic from Coordinator to reduce
its size and improve separation of concerns.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from ...const.config import CONF_PHONE_ID
from ..mqtt.credentials import decrypt_mqtt_credential
from ..mqtt.mqtt_client import LiproMqttClient
from .mqtt.setup import build_mqtt_subscription_device_ids, resolve_mqtt_biz_id
from .runtime.mqtt_runtime import MqttRuntime

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..api import LiproClient
    from ..device import LiproDevice
    from ..utils.background_task_manager import BackgroundTaskManager
    from .runtime.state_runtime import StateRuntime

_LOGGER = logging.getLogger(__name__)


class MqttListenerNotifier:
    """Notifier that triggers coordinator data updates on MQTT events."""

    def __init__(
        self,
        *,
        devices_getter: Callable[[], dict[str, LiproDevice]],
        set_updated_data: Callable[[dict[str, LiproDevice]], None],
    ) -> None:
        """Initialize notifier.

        Args:
            devices_getter: Function to get current devices dict
            set_updated_data: Function to trigger coordinator update
        """
        self._devices_getter = devices_getter
        self._set_updated_data = set_updated_data

    def schedule_listener_update(self) -> None:
        """Schedule a listener update (triggers coordinator refresh)."""
        self._set_updated_data(self._devices_getter())


class NoopConnectStateTracker:
    """No-op connect state tracker (placeholder for future implementation)."""

    def record_connect_state(
        self, device_serial: str, timestamp: float, is_online: bool
    ) -> None:
        """Record device connect state (no-op)."""


class NoopGroupReconciler:
    """No-op group reconciler (placeholder for future implementation)."""

    def schedule_group_reconciliation(
        self, device_name: str, timestamp: float
    ) -> None:
        """Schedule group reconciliation (no-op)."""


class PropertyApplierWrapper:
    """Wrapper to adapt function to PropertyApplierProtocol."""

    def __init__(
        self,
        apply_fn: Callable[
            [LiproDevice, dict[str, Any], str], Coroutine[Any, Any, bool]
        ],
    ) -> None:
        """Initialize wrapper."""
        self._apply_fn = apply_fn

    async def __call__(
        self,
        device: LiproDevice,
        properties: dict[str, Any],
        source: str,
    ) -> bool:
        """Apply properties update to device."""
        return await self._apply_fn(device, properties, source)


async def async_setup_mqtt(
    *,
    hass: HomeAssistant,
    client: LiproClient,
    config_entry: ConfigEntry,
    state_runtime: StateRuntime,
    background_task_manager: BackgroundTaskManager,
    devices: dict[str, LiproDevice],
    scan_interval_seconds: int,
    apply_properties_update: Callable[
        [LiproDevice, dict[str, Any], str], Coroutine[Any, Any, bool]
    ],
    set_updated_data: Callable[[dict[str, LiproDevice]], None],
) -> tuple[MqttRuntime, LiproMqttClient, str] | None:
    """Set up MQTT client for real-time updates.

    This function creates and initializes the MQTT client with credentials
    from the API, then starts the connection for current devices.

    Args:
        hass: Home Assistant instance
        client: Lipro API client
        config_entry: Configuration entry
        state_runtime: State runtime for device resolution
        background_task_manager: Background task manager
        devices: Current devices dict
        scan_interval_seconds: Polling interval in seconds
        apply_properties_update: Property update callback
        set_updated_data: Coordinator data update callback

    Returns:
        Tuple of (mqtt_runtime, mqtt_client, biz_id) on success, None on failure
    """
    try:
        # 10s timeout for MQTT config fetch
        try:
            async with asyncio.timeout(10):
                mqtt_config = await client.get_mqtt_config()
        except TimeoutError:
            _LOGGER.error("MQTT config fetch timeout after 10 seconds")
            return None

        if not mqtt_config:
            _LOGGER.warning("No MQTT config available")
            return None

        # Decrypt credentials
        access_key = decrypt_mqtt_credential(mqtt_config.get("accessKey", ""))
        secret_key = decrypt_mqtt_credential(mqtt_config.get("secretKey", ""))

        if not access_key or not secret_key:
            _LOGGER.warning("Failed to decrypt MQTT credentials")
            return None

        # Resolve biz_id
        biz_id = resolve_mqtt_biz_id(config_entry.data)
        if biz_id is None:
            _LOGGER.warning("No biz_id available for MQTT")
            return None

        phone_id = config_entry.data.get(CONF_PHONE_ID, "")

        # Create bridge function to connect sync callback to async handler
        def _on_message_bridge(topic: str, payload: dict[str, object]) -> None:
            """Bridge sync MQTT callback to async runtime handler."""
            # Schedule the async handler in the event loop
            asyncio.create_task(
                mqtt_runtime.handle_message(topic, payload),
                name=f"mqtt_message_{topic}",
            )

        # Create MQTT client with message callback bound to runtime
        mqtt_client = LiproMqttClient(
            access_key=access_key,
            secret_key=secret_key,
            biz_id=biz_id,
            phone_id=phone_id,
            on_message=_on_message_bridge,
        )

        # Create MQTT runtime with all dependencies injected at construction
        mqtt_runtime = MqttRuntime(
            hass=hass,
            mqtt_client=mqtt_client,
            base_scan_interval=scan_interval_seconds,
            device_resolver=state_runtime,
            property_applier=PropertyApplierWrapper(apply_properties_update),
            listener_notifier=MqttListenerNotifier(
                devices_getter=lambda: devices,
                set_updated_data=set_updated_data,
            ),
            connect_state_tracker=NoopConnectStateTracker(),
            group_reconciler=NoopGroupReconciler(),
            polling_multiplier=2,
            background_task_manager=background_task_manager,
        )

        # Start MQTT connection for current devices with 15s timeout
        # Use helper function that provides fallback to all devices if no groups
        device_ids = build_mqtt_subscription_device_ids(devices)
        if device_ids:
            try:
                async with asyncio.timeout(15):
                    await mqtt_runtime.connect(device_ids=device_ids, biz_id=biz_id)
            except TimeoutError:
                _LOGGER.error("MQTT connection timeout after 15 seconds")
                return None

        # Verify connection state before returning success
        if not mqtt_runtime.is_connected:
            _LOGGER.warning("MQTT client not connected after setup")
            return None

        return (mqtt_runtime, mqtt_client, biz_id)

    except Exception:
        _LOGGER.exception("Failed to setup MQTT")
        return None


__all__ = [
    "MqttListenerNotifier",
    "NoopConnectStateTracker",
    "NoopGroupReconciler",
    "async_setup_mqtt",
]
