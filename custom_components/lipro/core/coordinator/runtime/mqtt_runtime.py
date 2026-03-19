"""MQTT runtime implementation with protocol compliance.

This module implements the composed MQTT runtime using independent
components without inheriting from _CoordinatorBase.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping
import logging
from time import monotonic
from typing import TYPE_CHECKING, Any, Protocol, TypeVar

from homeassistant.helpers.issue_registry import (
    IssueSeverity,
    async_create_issue,
    async_delete_issue,
)

from ....const.api import MQTT_DISCONNECT_NOTIFY_THRESHOLD
from ....const.base import DOMAIN
from ...telemetry.models import (
    FailureSummary,
    build_failure_summary_from_exception,
    empty_failure_summary,
)
from .mqtt.adapters import (
    ConnectStateTrackerProtocol,
    DeviceResolverProtocol,
    GroupReconcilerProtocol,
    ListenerNotifierProtocol,
    PropertyApplierProtocol,
    build_mqtt_message_handler,
)
from .mqtt.connection import MqttConnectionManager, PollingIntervalUpdater
from .mqtt.dedup import MqttDedupManager
from .mqtt.message_handler import MqttMessageHandler
from .mqtt.reconnect import MqttReconnectManager

if TYPE_CHECKING:
    from collections.abc import Coroutine

    from homeassistant.core import HomeAssistant

    from ...protocol import MqttTransportFacade
    from ..types import PropertyValue

_LOGGER = logging.getLogger(__name__)
_ResultT = TypeVar("_ResultT")


class BackgroundTaskManagerProtocol(Protocol):
    """Minimal background-task surface consumed by MQTT runtime."""

    def create(
        self,
        coro: Coroutine[Any, Any, Any],
        *,
        create_task: Callable[[Coroutine[Any, Any, Any]], asyncio.Task[Any]] | None = None,
    ) -> asyncio.Task[Any]:
        """Create and track one background task."""
        ...


class MqttRuntime:
    """Standalone MQTT runtime using dependency injection."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        mqtt_transport: MqttTransportFacade | None,
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
        background_task_manager: BackgroundTaskManagerProtocol | None = None,
    ) -> None:
        """Initialize MQTT runtime with all dependencies injected at construction.

        Args:
            hass: Home Assistant instance
            mqtt_transport: MQTT transport instance (can be None initially)
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
        self._mqtt_transport = mqtt_transport
        self._base_scan_interval = base_scan_interval
        self._background_task_manager = background_task_manager
        self._last_transport_error: Exception | None = None
        self._last_transport_error_stage: str | None = None
        self._failure_summary: FailureSummary = empty_failure_summary()

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

    async def _async_run_transport_operation(
        self,
        *,
        stage: str,
        action: str,
        operation: Callable[[], Awaitable[_ResultT]],
    ) -> tuple[bool, _ResultT | None]:
        """Run one transport operation with explicit failure recording."""
        try:
            return True, await operation()
        except asyncio.CancelledError:
            raise
        except (
            TimeoutError,
            OSError,
            RuntimeError,
            ValueError,
            TypeError,
            LookupError,
        ) as err:
            self.handle_transport_error(err, stage=stage)
            _LOGGER.exception("MQTT %s failed", action)
            return False, None

    def bind_transport(self, mqtt_transport: MqttTransportFacade) -> None:
        """Bind one protocol-owned MQTT transport to this runtime."""
        self._mqtt_transport = mqtt_transport
        self._last_transport_error = None
        self._last_transport_error_stage = None
        self._failure_summary = empty_failure_summary()

    def detach_transport(self) -> None:
        """Detach the currently bound MQTT transport from this runtime."""
        self._mqtt_transport = None

    @property
    def has_transport(self) -> bool:
        """Return whether one MQTT transport is currently bound."""
        return self._mqtt_transport is not None

    def _create_message_handler(self) -> MqttMessageHandler:
        """Create message handler with injected dependencies."""
        return build_mqtt_message_handler(
            device_resolver=self._device_resolver,
            property_applier=self._property_applier,
            listener_notifier=self._listener_notifier,
            connect_state_tracker=self._connect_state_tracker,
            group_reconciler=self._group_reconciler,
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

        if self._mqtt_transport is None:
            _LOGGER.error("MQTT transport not initialized")
            return False

        mqtt_transport = self._mqtt_transport

        async def _connect_sequence() -> bool:
            await mqtt_transport.start(device_ids)
            await mqtt_transport.sync_subscriptions(set(device_ids))
            return await mqtt_transport.wait_until_connected()

        ok, connected = await self._async_run_transport_operation(
            stage="connect",
            action="connection",
            operation=_connect_sequence,
        )
        if not ok:
            self._reconnect_manager.on_reconnect_failure()
            return False

        if connected:
            return True

        self._reconnect_manager.on_reconnect_failure()
        return False

    async def sync_subscriptions(self, device_ids: list[str] | set[str]) -> bool:
        """Synchronize the desired MQTT subscription set without reconnecting."""
        if self._mqtt_transport is None:
            return False

        mqtt_transport = self._mqtt_transport

        async def _sync_operation() -> None:
            await mqtt_transport.sync_subscriptions(set(device_ids))

        ok, _ = await self._async_run_transport_operation(
            stage="sync_subscriptions",
            action="subscription sync",
            operation=_sync_operation,
        )
        if not ok:
            return False

        return True

    async def disconnect(self) -> None:
        """Stop the MQTT background loop."""
        if self._mqtt_transport is None:
            return

        try:
            await self._async_run_transport_operation(
                stage="disconnect",
                action="disconnect",
                operation=self._mqtt_transport.stop,
            )
        finally:
            self.on_transport_disconnected()

    async def handle_message(
        self,
        device_id: str,
        properties: Mapping[str, PropertyValue],
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

    def handle_transport_error(
        self,
        err: Exception,
        *,
        stage: str = "transport",
    ) -> None:
        """Record transport-level errors for diagnostics without mutating state."""
        self._last_transport_error = err
        self._last_transport_error_stage = stage
        self._failure_summary = build_failure_summary_from_exception(
            err,
            failure_origin="runtime.mqtt",
        )
        _LOGGER.debug(
            "MQTT transport reported error (%s) during %s",
            type(err).__name__,
            stage,
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
        self._last_transport_error_stage = None
        self._failure_summary = empty_failure_summary()

    @property
    def is_connected(self) -> bool:
        """Return current MQTT connection state."""
        return self._connection_manager.is_connected

    def get_runtime_metrics(self) -> dict[str, object]:
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
            "last_transport_error_stage": self._last_transport_error_stage,
            "failure_summary": dict(self._failure_summary),
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
