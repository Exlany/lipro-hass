"""MQTT message handling and device update logic."""

from __future__ import annotations

import logging
from time import monotonic
from typing import TYPE_CHECKING, Any, Protocol

from .....const.properties import PROP_CONNECT_STATE
from ....mqtt.message import is_online_connect_state

if TYPE_CHECKING:
    from ....device import LiproDevice


class DeviceResolver(Protocol):
    """Protocol for resolving devices by ID."""

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Get device by ID."""
        ...


class PropertyApplier(Protocol):
    """Protocol for applying property updates to devices."""

    def apply_properties_update(
        self, device: LiproDevice, properties: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply properties update and return applied properties."""
        ...


class ListenerNotifier(Protocol):
    """Protocol for notifying listeners of updates."""

    def schedule_listener_update(self) -> None:
        """Schedule a listener update."""
        ...


class ConnectStateTracker(Protocol):
    """Protocol for tracking device connect state."""

    def record_connect_state(
        self, device_serial: str, timestamp: float, is_online: bool
    ) -> None:
        """Record connect state observation."""
        ...


class GroupReconciler(Protocol):
    """Protocol for scheduling group reconciliation."""

    def schedule_group_reconciliation(
        self, device_name: str, timestamp: float
    ) -> None:
        """Schedule group online reconciliation."""
        ...


class MqttMessageHandler:
    """Handles MQTT message processing and device updates."""

    def __init__(
        self,
        *,
        device_resolver: DeviceResolver,
        property_applier: PropertyApplier,
        listener_notifier: ListenerNotifier,
        connect_state_tracker: ConnectStateTracker,
        group_reconciler: GroupReconciler,
        logger: logging.Logger,
    ) -> None:
        """Initialize message handler."""
        self._device_resolver = device_resolver
        self._property_applier = property_applier
        self._listener_notifier = listener_notifier
        self._connect_state_tracker = connect_state_tracker
        self._group_reconciler = group_reconciler
        self._logger = logger

    def handle_message(
        self,
        device_id: str,
        properties: dict[str, Any],
        *,
        current_time: float | None = None,
    ) -> bool:
        """Handle incoming MQTT message with device status update."""
        device = self._device_resolver.get_device_by_id(device_id)
        if device is None:
            self._logger.debug(
                "Ignoring MQTT message for unknown device: %s", device_id
            )
            return False

        if not properties:
            return False

        applied = self._property_applier.apply_properties_update(device, properties)
        if not applied:
            return False

        now = monotonic() if current_time is None else current_time
        self._after_properties_applied(device, applied, current_time=now)
        return True

    def _after_properties_applied(
        self,
        device: LiproDevice,
        properties: dict[str, Any],
        *,
        current_time: float,
    ) -> None:
        """Run post-update notifications and reconciliation hooks."""
        if not properties:
            return

        self._listener_notifier.schedule_listener_update()

        connect_state = properties.get(PROP_CONNECT_STATE)
        if connect_state is not None:
            is_online = is_online_connect_state(connect_state)
            self._connect_state_tracker.record_connect_state(
                device.serial, current_time, is_online
            )

            if device.is_group and is_online:
                self._group_reconciler.schedule_group_reconciliation(
                    device.name, current_time
                )
