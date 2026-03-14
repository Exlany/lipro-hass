"""MQTT runtime implementation with protocol compliance.

This module implements the composed MQTT runtime using independent
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
from .mqtt.connection import MqttConnectionManager, PollingIntervalUpdater
from .mqtt.dedup import MqttDedupManager
from .mqtt.message_handler import MqttMessageHandler
from .mqtt.reconnect import MqttReconnectManager

if TYPE_CHECKING:
    from collections.abc import Coroutine

    from homeassistant.core import HomeAssistant

    from ...device import LiproDevice
    from ...protocol import MqttTransportFacade

_LOGGER = logging.getLogger(__name__)


class DeviceResolverProtocol(Protocol):
    """Protocol for device resolution."""

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Resolve device by ID."""
        ...


class PropertyApplierProtocol(Protocol):
    """Protocol for property application."""

    async def __call__(
        self,
        device: LiproDevice,
        properties: dict[str, Any],
        source: str,
    ) -> bool:
        """Apply properties update to device."""
        ...


class ListenerNotifierProtocol(Protocol):
    """Protocol for listener notification."""

    def schedule_listener_update(self) -> None:
        """Schedule a listener update."""
        ...


class ConnectStateTrackerProtocol(Protocol):
    """Protocol for connect state tracking."""

    def record_connect_state(
        self, device_serial: str, timestamp: float, is_online: bool
    ) -> None:
        """Record connect state observation."""
        ...


class GroupReconcilerProtocol(Protocol):
    """Protocol for group reconciliation."""

    def schedule_group_reconciliation(self, device_name: str, timestamp: float) -> None:
        """Schedule group online reconciliation."""
        ...


class MqttRuntime:
    """Standalone MQTT runtime using dependency injection."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        mqtt_client: MqttTransportFacade | None,
        base_scan_interval: int,
        polling_updater: PollingIntervalUpdater,
        device_resolver: DeviceResolverProtocol,
        property_applier: PropertyApplierProtocol,
        listener_notifier: ListenerNotifierProtocol,
        connect_state_tracker: ConnectStateTrackerProtocol,
        group_reconciler: GroupReconcilerProtocol,
        polling_multiplier: int = 2,
        dedup_window: float = 0.5,
        reconnect_base_delay: float = 1.0,
        reconnect_max_delay: float = 60.0,
        background_task_manager: Any | None = None,
    ) -> None:
        """Initialize MQTT runtime with all dependencies injected at construction.

        Args:
            hass: Home Assistant instance
            mqtt_client: MQTT client instance (can be None initially)
            base_scan_interval: Base polling interval in seconds
            device_resolver: Device resolution protocol implementation
            property_applier: Property application protocol implementation
            listener_notifier: Listener notification protocol implementation
            connect_state_tracker: Connect state tracking protocol implementation
            group_reconciler: Group reconciliation protocol implementation
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
        self._last_transport_error: Exception | None = None

        self._device_resolver = device_resolver
        self._property_applier = property_applier
        self._listener_notifier = listener_notifier
        self._connect_state_tracker = connect_state_tracker
        self._group_reconciler = group_reconciler

        self._connection_manager = MqttConnectionManager(
            hass=hass,
            polling_updater=polling_updater,
            base_scan_interval=base_scan_interval,
            polling_multiplier=polling_multiplier,
            logger=_LOGGER,
        )

        self._dedup_manager = MqttDedupManager(dedup_window=dedup_window)

        self._reconnect_manager = MqttReconnectManager(
            base_delay=reconnect_base_delay,
            max_delay=reconnect_max_delay,
        )

        self._message_handler = self._create_message_handler()

    def bind_transport(self, mqtt_client: MqttTransportFacade) -> None:
        """Bind one protocol-owned MQTT transport to this runtime."""
        self._mqtt_client = mqtt_client
        self._last_transport_error = None

    def detach_transport(self) -> None:
        """Detach the currently bound MQTT transport from this runtime."""
        self._mqtt_client = None

    @property
    def has_transport(self) -> bool:
        """Return whether one MQTT transport is currently bound."""
        return self._mqtt_client is not None

    def _create_message_handler(self) -> MqttMessageHandler:
        """Create message handler with injected dependencies."""

        class DeviceResolverAdapter:
            """Adapter for callable-or-object device resolution ports."""

            def __init__(self, resolver: DeviceResolverProtocol) -> None:
                self._resolver = resolver

            def get_device_by_id(self, device_id: str) -> LiproDevice | None:
                resolver = self._resolver
                method = getattr(resolver, "get_device_by_id", None)
                if callable(method):
                    return method(device_id)
                return resolver(device_id)

        class PropertyApplierAdapter:
            """Adapter to convert bool-returning applier to dict-returning."""

            def __init__(self, applier: PropertyApplierProtocol) -> None:
                self._applier = applier

            async def apply_properties_update(
                self, device: LiproDevice, properties: dict[str, Any]
            ) -> dict[str, Any]:
                """Apply properties and return applied dict."""
                success = await self._applier(device, properties, "mqtt")
                return properties if success else {}

        class ListenerNotifierAdapter:
            """Adapter for callable-or-object listener notification ports."""

            def __init__(self, notifier: ListenerNotifierProtocol) -> None:
                self._notifier = notifier

            def schedule_listener_update(self) -> None:
                notifier = self._notifier
                method = getattr(notifier, "schedule_listener_update", None)
                if callable(method):
                    method()
                    return
                notifier()

        class ConnectStateTrackerAdapter:
            """Adapter for callable-or-object connect-state tracking ports."""

            def __init__(self, tracker: ConnectStateTrackerProtocol) -> None:
                self._tracker = tracker

            def record_connect_state(
                self, device_serial: str, timestamp: float, is_online: bool
            ) -> None:
                tracker = self._tracker
                method = getattr(tracker, "record_connect_state", None)
                if callable(method):
                    method(device_serial, timestamp, is_online)
                    return
                tracker(device_serial, timestamp, is_online)

        class GroupReconcilerAdapter:
            """Adapter for callable-or-object group reconciliation ports."""

            def __init__(self, reconciler: GroupReconcilerProtocol) -> None:
                self._reconciler = reconciler

            def schedule_group_reconciliation(
                self, device_name: str, timestamp: float
            ) -> None:
                reconciler = self._reconciler
                method = getattr(reconciler, "schedule_group_reconciliation", None)
                if callable(method):
                    method(device_name, timestamp)
                    return
                reconciler(device_name, timestamp)

        return MqttMessageHandler(
            device_resolver=DeviceResolverAdapter(self._device_resolver),
            property_applier=PropertyApplierAdapter(self._property_applier),
            listener_notifier=ListenerNotifierAdapter(self._listener_notifier),
            connect_state_tracker=ConnectStateTrackerAdapter(self._connect_state_tracker),
            group_reconciler=GroupReconcilerAdapter(self._group_reconciler),
            logger=_LOGGER,
        )

    async def connect(
        self,
        *,
        device_ids: list[str],
    ) -> bool:
        """Start the MQTT background loop and wait for real transport connection.

        Args:
            device_ids: List of device identifiers to subscribe to.

        Returns:
            True if startup succeeded and the broker handshake completed.
        """

        if self._mqtt_client is None:
            _LOGGER.error("MQTT client not initialized")
            return False

        try:
            await self._mqtt_client.start(device_ids)
            await self._mqtt_client.sync_subscriptions(set(device_ids))
            connected = await self._mqtt_client.wait_until_connected()
        except Exception as err:
            if isinstance(err, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
                raise
            _LOGGER.exception("MQTT connection failed")
            self._reconnect_manager.on_reconnect_failure()
            return False

        if connected:
            return True

        self._reconnect_manager.on_reconnect_failure()
        return False

    async def sync_subscriptions(self, device_ids: list[str] | set[str]) -> bool:
        """Synchronize the desired MQTT subscription set without reconnecting."""
        if self._mqtt_client is None:
            return False

        try:
            await self._mqtt_client.sync_subscriptions(set(device_ids))
        except Exception as err:
            if isinstance(err, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
                raise
            _LOGGER.exception("Failed to sync MQTT subscriptions")
            return False

        return True

    async def disconnect(self) -> None:
        """Stop the MQTT background loop."""
        if self._mqtt_client is None:
            return

        try:
            await self._mqtt_client.stop()
        except Exception as err:
            if isinstance(err, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
                raise
            _LOGGER.exception("MQTT disconnect failed")
        finally:
            self.on_transport_disconnected()

    async def handle_message(
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

        if self._dedup_manager.is_duplicate(
            device_id, properties, current_time=current_time
        ):
            return

        await self._message_handler.handle_message(device_id, properties, current_time=current_time)
        self._dedup_manager.cleanup(current_time=current_time)

    def on_transport_connected(self) -> None:
        """Apply coordinator-facing state changes after a real broker handshake."""
        had_disconnect_state = (
            self._connection_manager.disconnect_notified
            or self._connection_manager.disconnect_time is not None
        )
        if not self._connection_manager.is_connected:
            self._connection_manager.on_connect()
        self._reconnect_manager.on_reconnect_success()
        if had_disconnect_state:
            self._track_background_task(
                self.clear_disconnect_notification(),
                name="lipro_mqtt_clear_issue",
            )

    def on_transport_disconnected(self) -> None:
        """Apply coordinator-facing state changes after transport teardown."""
        if (
            not self._connection_manager.is_connected
            and self._connection_manager.disconnect_time is not None
        ):
            return
        self._connection_manager.on_disconnect()

    def handle_transport_error(self, err: Exception) -> None:
        """Record transport-level errors for diagnostics without mutating state."""
        self._last_transport_error = err
        _LOGGER.debug(
            "MQTT transport reported error (%s)",
            type(err).__name__,
        )

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
                self._track_background_task(
                    self._async_show_mqtt_disconnect_notification(minutes),
                    name="lipro_mqtt_disconnect_issue",
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
        self._last_transport_error = None

    @property
    def is_connected(self) -> bool:
        """Return current MQTT connection state."""
        return self._connection_manager.is_connected

    def get_runtime_metrics(self) -> dict[str, Any]:
        """Return lightweight MQTT runtime telemetry."""
        last_transport_error = self._last_transport_error
        return {
            "has_transport": self.has_transport,
            "is_connected": self._connection_manager.is_connected,
            "disconnect_time": self._connection_manager.disconnect_time,
            "disconnect_notified": self._connection_manager.disconnect_notified,
            "last_transport_error": (
                type(last_transport_error).__name__ if last_transport_error is not None else None
            ),
            "backoff_gate_logged": self._reconnect_manager.backoff_gate_logged,
        }

    def _track_background_task(
        self,
        coro: Coroutine[Any, Any, Any],
        *,
        name: str,
    ) -> None:
        """Track one runtime-owned background task with safe exception handling."""
        if self._background_task_manager is not None:
            self._background_task_manager.create(
                coro,
                create_task=lambda candidate: asyncio.create_task(candidate, name=name),
            )
            return

        task = asyncio.create_task(coro, name=name)
        task.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)


__all__ = ["MqttRuntime"]
