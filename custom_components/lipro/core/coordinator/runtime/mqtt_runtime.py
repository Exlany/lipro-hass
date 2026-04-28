"""MQTT runtime implementation with protocol compliance.

This module implements the composed MQTT runtime using independent
components without inheriting from _CoordinatorBase.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
import logging
from time import monotonic
from typing import TYPE_CHECKING, Protocol

from homeassistant.helpers.issue_registry import (
    IssueSeverity,
    async_create_issue,
    async_delete_issue,
)

from ....const.base import DOMAIN
from ...telemetry.models import (
    FailureSummary,
    OperationOutcome,
    build_failure_summary_from_exception,
    build_operation_outcome,
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
from .mqtt_runtime_support import (
    build_runtime_metrics,
    consume_background_task_exception,
    disconnect_notification_minutes,
    finalize_connect_attempt,
    had_disconnect_state,
    require_transport,
    run_transport_operation,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from homeassistant.core import HomeAssistant

    from ...protocol import MqttTransportFacade
    from ..types import PropertyValue, RuntimeMetrics
    from .mqtt_runtime_support import _TransportFacadeProtocol

_LOGGER = logging.getLogger(__name__)


class BackgroundTaskManagerProtocol(Protocol):
    """Minimal background-task surface consumed by MQTT runtime."""

    def create(
        self,
        coro: Coroutine[object, object, object],
        *,
        create_task: Callable[[Coroutine[object, object, object]], asyncio.Task[object]]
        | None = None,
    ) -> asyncio.Task[object]:
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
        """Initialize MQTT runtime with all dependencies injected at construction."""
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

    async def _await_transport_connection(
        self,
        *,
        mqtt_transport: _TransportFacadeProtocol,
        device_ids: list[str],
    ) -> bool:
        """Run the concrete transport connect sequence through the runtime guard."""

        async def _connect_sequence() -> bool:
            await mqtt_transport.start(device_ids)
            await mqtt_transport.sync_subscriptions(set(device_ids))
            return await mqtt_transport.wait_until_connected()

        ok, connected = await run_transport_operation(
            stage="connect",
            action="connection",
            operation=_connect_sequence,
            handle_transport_error=lambda err: self.handle_transport_error(
                err, stage="connect"
            ),
            logger=_LOGGER,
        )
        return bool(ok and connected)

    async def connect(
        self,
        *,
        device_ids: list[str],
    ) -> bool:
        """Start the MQTT background loop and wait for real transport connection."""
        mqtt_transport = require_transport(
            self._mqtt_transport,
            logger=_LOGGER,
            log_missing=True,
        )
        if mqtt_transport is None:
            return False
        connected = await self._await_transport_connection(
            mqtt_transport=mqtt_transport,
            device_ids=device_ids,
        )
        return finalize_connect_attempt(
            connected=connected,
            reconnect_manager=self._reconnect_manager,
        )

    async def sync_subscriptions(self, device_ids: list[str] | set[str]) -> bool:
        """Synchronize the desired MQTT subscription set without reconnecting."""
        mqtt_transport = require_transport(self._mqtt_transport, logger=_LOGGER)
        if mqtt_transport is None:
            return False

        async def _sync_operation() -> None:
            await mqtt_transport.sync_subscriptions(set(device_ids))

        ok, _ = await run_transport_operation(
            stage="sync_subscriptions",
            action="subscription sync",
            operation=_sync_operation,
            handle_transport_error=lambda err: self.handle_transport_error(
                err, stage="sync_subscriptions"
            ),
            logger=_LOGGER,
        )
        return bool(ok)

    async def disconnect(self) -> None:
        """Stop the MQTT background loop."""
        mqtt_transport = require_transport(self._mqtt_transport, logger=_LOGGER)
        if mqtt_transport is None:
            return

        try:
            await run_transport_operation(
                stage="disconnect",
                action="disconnect",
                operation=mqtt_transport.stop,
                handle_transport_error=lambda err: self.handle_transport_error(
                    err, stage="disconnect"
                ),
                logger=_LOGGER,
            )
        finally:
            self.on_transport_disconnected()

    async def handle_message(
        self,
        device_id: str,
        properties: Mapping[str, PropertyValue],
    ) -> OperationOutcome:
        """Handle incoming MQTT message and return one typed application outcome."""
        current_time = monotonic()
        if self._dedup_manager.is_duplicate(
            device_id, properties, current_time=current_time
        ):
            return build_operation_outcome(
                kind="skipped",
                reason_code="duplicate_message",
            )

        outcome = await self._message_handler.handle_message(
            device_id,
            properties,
            current_time=current_time,
        )
        self._dedup_manager.cleanup(current_time=current_time)
        return outcome

    def on_transport_connected(self) -> None:
        """Apply coordinator-facing state changes after a real broker handshake."""
        had_disconnect = had_disconnect_state(self._connection_manager)
        if not self._connection_manager.is_connected:
            self._connection_manager.on_connect()
        self._reconnect_manager.on_reconnect_success()
        if had_disconnect:
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
        """Check if reconnection should be attempted."""
        return self._reconnect_manager.should_attempt_reconnect()

    def _schedule_disconnect_notification(self, minutes: int) -> None:
        """Persist and emit one disconnect notification task."""
        self._connection_manager.mark_disconnect_notified()
        self._track_background_task(
            self._async_show_mqtt_disconnect_notification(minutes),
            name="lipro_mqtt_disconnect_issue",
        )

    def check_disconnect_notification(self) -> None:
        """Check if disconnect notification should be sent."""
        minutes = disconnect_notification_minutes(
            connection_manager=self._connection_manager,
        )
        if minutes is None:
            return
        self._schedule_disconnect_notification(minutes)

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

    def get_runtime_metrics(self) -> RuntimeMetrics:
        """Return lightweight MQTT runtime telemetry."""
        return build_runtime_metrics(
            has_transport=self.has_transport,
            connection_manager=self._connection_manager,
            last_transport_error=self._last_transport_error,
            last_transport_error_stage=self._last_transport_error_stage,
            failure_summary=self._failure_summary,
            reconnect_manager=self._reconnect_manager,
        )

    def _track_background_task(
        self,
        coro: Coroutine[object, object, object],
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
        task.add_done_callback(consume_background_task_exception)


__all__ = ["MqttRuntime"]
