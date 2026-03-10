"""MQTT runtime implementation with protocol compliance.

This module implements MqttRuntimeProtocol using composition of independent
components without inheriting from _CoordinatorBase.
"""

from __future__ import annotations

import asyncio
import logging
from time import monotonic
from typing import TYPE_CHECKING, Any, Protocol

from homeassistant.helpers.issue_registry import (
    IssueSeverity,
    async_create_issue,
    async_delete_issue,
)

from ....const.api import MQTT_DISCONNECT_NOTIFY_THRESHOLD
from ....const.base import DOMAIN
from .mqtt.connection import MqttConnectionManager
from .mqtt.dedup import MqttDedupManager
from .mqtt.message_handler import MqttMessageHandler
from .mqtt.reconnect import MqttReconnectManager

if TYPE_CHECKING:
    from datetime import timedelta

    from homeassistant.core import HomeAssistant

    from ....mqtt.client import LiproMqttClient
    from ...device import LiproDevice

_LOGGER = logging.getLogger(__name__)


class DeviceResolverProtocol(Protocol):
    """Protocol for device resolution."""

    def __call__(self, device_id: str) -> LiproDevice | None:
        """Resolve device by ID."""
        ...


class PropertyApplierProtocol(Protocol):
    """Protocol for property application."""

    def __call__(
        self,
        device: LiproDevice,
        properties: dict[str, Any],
        source: str,
    ) -> bool:
        """Apply properties update to device."""
        ...


class ListenerNotifierProtocol(Protocol):
    """Protocol for listener notification."""

    def __call__(self) -> None:
        """Notify listeners of state changes."""
        ...


class ConnectStateTrackerProtocol(Protocol):
    """Protocol for connect state tracking."""

    def __call__(self, device_id: str) -> None:
        """Track device connect state priority."""
        ...


class GroupReconcilerProtocol(Protocol):
    """Protocol for group reconciliation."""

    def __call__(self, group_id: str) -> None:
        """Reconcile group state."""
        ...


class MqttRuntime:
    """Standalone MQTT runtime using dependency injection."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        mqtt_client: LiproMqttClient | None,
        base_scan_interval: int,
        polling_multiplier: int = 2,
        dedup_window: float = 0.5,
        reconnect_base_delay: float = 1.0,
        reconnect_max_delay: float = 60.0,
        background_task_manager: Any | None = None,
    ) -> None:
        """Initialize MQTT runtime with injected dependencies.

        Args:
            hass: Home Assistant instance
            mqtt_client: MQTT client instance (can be None initially)
            base_scan_interval: Base polling interval in seconds
            polling_multiplier: Multiplier for relaxed polling when MQTT connected
            dedup_window: Deduplication time window in seconds
            reconnect_base_delay: Base delay for reconnection backoff
            reconnect_max_delay: Maximum delay for reconnection backoff
            background_task_manager: Optional background task manager for tracking tasks
        """
        self._hass = hass
        self._mqtt_client = mqtt_client
        self._base_scan_interval = base_scan_interval
        self._background_task_manager = background_task_manager

        # Polling interval updater will be injected via set_polling_updater
        self._polling_updater: Any = None

        # Device resolver, property applier, etc. will be injected
        self._device_resolver: DeviceResolverProtocol | None = None
        self._property_applier: PropertyApplierProtocol | None = None
        self._listener_notifier: ListenerNotifierProtocol | None = None
        self._connect_state_tracker: ConnectStateTrackerProtocol | None = None
        self._group_reconciler: GroupReconcilerProtocol | None = None

        # Initialize component managers
        self._connection_manager = MqttConnectionManager(
            hass=hass,
            polling_updater=self,  # Self implements PollingIntervalUpdater
            base_scan_interval=base_scan_interval,
            polling_multiplier=polling_multiplier,
            logger=_LOGGER,
        )

        self._dedup_manager = MqttDedupManager(dedup_window=dedup_window)

        self._reconnect_manager = MqttReconnectManager(
            base_delay=reconnect_base_delay,
            max_delay=reconnect_max_delay,
        )

        # Message handler will be initialized after dependencies are injected
        self._message_handler: MqttMessageHandler | None = None

    def set_polling_updater(self, updater: Any) -> None:
        """Inject polling interval updater dependency."""
        self._polling_updater = updater

    def set_device_resolver(self, resolver: DeviceResolverProtocol) -> None:
        """Inject device resolver dependency."""
        self._device_resolver = resolver

    def set_property_applier(self, applier: PropertyApplierProtocol) -> None:
        """Inject property applier dependency."""
        self._property_applier = applier

    def set_listener_notifier(self, notifier: ListenerNotifierProtocol) -> None:
        """Inject listener notifier dependency."""
        self._listener_notifier = notifier

    def set_connect_state_tracker(self, tracker: ConnectStateTrackerProtocol) -> None:
        """Inject connect state tracker dependency."""
        self._connect_state_tracker = tracker

    def set_group_reconciler(self, reconciler: GroupReconcilerProtocol) -> None:
        """Inject group reconciler dependency."""
        self._group_reconciler = reconciler

    def _ensure_message_handler(self) -> MqttMessageHandler:
        """Lazy initialize message handler after dependencies are injected."""
        if self._message_handler is None:
            if not all(
                [
                    self._device_resolver,
                    self._property_applier,
                    self._listener_notifier,
                    self._connect_state_tracker,
                    self._group_reconciler,
                ]
            ):
                msg = "Message handler dependencies not fully injected"
                raise RuntimeError(msg)

            self._message_handler = MqttMessageHandler(
                device_resolver=self._device_resolver,
                property_applier=self._property_applier,
                listener_notifier=self._listener_notifier,
                connect_state_tracker=self._connect_state_tracker,
                group_reconciler=self._group_reconciler,
                logger=_LOGGER,
            )
        return self._message_handler

    def update_polling_interval(self, interval: timedelta) -> None:
        """Update polling interval via injected updater."""
        if self._polling_updater is not None:
            self._polling_updater.update_interval = interval

    async def setup(self) -> bool:
        """Set up MQTT connection (no-op if client not initialized).

        This is a compatibility method for coordinator integration.
        The actual MQTT client setup happens in coordinator.async_setup_mqtt().

        Returns:
            True if MQTT client is available, False otherwise
        """
        if self._mqtt_client is None:
            _LOGGER.debug("MQTT client not initialized, skipping setup")
            return False
        return True

    async def connect(
        self,
        *,
        device_ids: list[str],
        biz_id: str,
    ) -> bool:
        """Connect to MQTT broker and subscribe to device topics.

        Args:
            device_ids: List of device IDs to subscribe to
            biz_id: Business ID for MQTT topics

        Returns:
            True if connection succeeded, False otherwise
        """
        if self._mqtt_client is None:
            _LOGGER.error("MQTT client not initialized")
            return False

        try:
            await self._mqtt_client.connect()
            await self._mqtt_client.subscribe_devices(device_ids, biz_id)
            self._connection_manager.on_connect()
            self._reconnect_manager.on_reconnect_success()
            return True
        except Exception as err:
            if isinstance(err, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
                raise
            _LOGGER.exception("MQTT connection failed")
            self._reconnect_manager.on_reconnect_failure()
            return False

    async def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        if self._mqtt_client is None:
            return

        try:
            await self._mqtt_client.disconnect()
        except Exception as err:
            if isinstance(err, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
                raise
            _LOGGER.exception("MQTT disconnect failed")
        finally:
            self._connection_manager.on_disconnect()

    def handle_message(
        self,
        device_id: str,
        properties: dict[str, Any],
    ) -> None:
        """Handle incoming MQTT message.

        Args:
            device_id: Device identifier from MQTT topic
            properties: Property updates from message payload
        """
        current_time = monotonic()

        # Check for duplicates
        if self._dedup_manager.is_duplicate(
            device_id, properties, current_time=current_time
        ):
            return

        # Process message
        handler = self._ensure_message_handler()
        handler.handle_message(device_id, properties, current_time=current_time)

        # Periodic cleanup
        self._dedup_manager.cleanup(current_time=current_time)

    def should_attempt_reconnect(self) -> bool:
        """Check if reconnection should be attempted.

        Returns:
            True if reconnection should be attempted, False if in backoff period
        """
        return self._reconnect_manager.should_attempt_reconnect()

    def check_disconnect_notification(self) -> None:
        """Check if disconnect notification should be sent."""
        if not self._connection_manager.is_connected:
            disconnect_time = self._connection_manager.disconnect_time
            if disconnect_time is None:
                return

            elapsed = monotonic() - disconnect_time
            if (
                elapsed >= MQTT_DISCONNECT_NOTIFY_THRESHOLD
                and not self._connection_manager.disconnect_notified
            ):
                minutes = int(elapsed // 60)
                self._connection_manager.mark_disconnect_notified()
                # Create notification task with proper tracking
                if self._background_task_manager:
                    self._background_task_manager.create(
                        self._async_show_mqtt_disconnect_notification(minutes)
                    )
                else:
                    # Fallback to untracked task if no manager available
                    task = asyncio.create_task(
                        self._async_show_mqtt_disconnect_notification(minutes)
                    )
                    task.add_done_callback(
                        lambda t: t.exception() if not t.cancelled() else None
                    )

    async def _async_show_mqtt_disconnect_notification(self, minutes: int) -> None:
        """Create a repair issue for MQTT disconnect."""
        async_create_issue(
            self._hass,
            domain=DOMAIN,
            issue_id="mqtt_disconnected",
            is_fixable=False,
            severity=IssueSeverity.WARNING,
            translation_key="mqtt_disconnected",
            translation_placeholders={"minutes": str(minutes)},
        )

    async def clear_disconnect_notification(self) -> None:
        """Clear MQTT disconnect notification."""
        async_delete_issue(self._hass, domain=DOMAIN, issue_id="mqtt_disconnected")

    def reset(self) -> None:
        """Reset all runtime state."""
        self._connection_manager.reset()
        self._dedup_manager.reset()
        self._reconnect_manager.reset()

    @property
    def is_connected(self) -> bool:
        """Return current MQTT connection state."""
        return self._connection_manager.is_connected


__all__ = ["MqttRuntime"]
