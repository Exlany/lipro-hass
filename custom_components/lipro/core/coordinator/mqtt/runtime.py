"""Coordinator-side MQTT runtime helpers.

This module intentionally operates on the coordinator instance to keep the
extracted logic behavior-identical while shrinking coordinator method bodies.
"""
# ruff: noqa: SLF001

from __future__ import annotations

from datetime import timedelta
import logging
from time import monotonic
from typing import TYPE_CHECKING

from ....const.api import MQTT_DISCONNECT_NOTIFY_THRESHOLD
from .policy import (
    resolve_disconnect_notification_minutes,
    resolve_disconnect_started_at,
)
from .polling import (
    resolve_polling_interval_seconds_on_mqtt_connect,
    resolve_polling_interval_seconds_on_mqtt_disconnect,
)

if TYPE_CHECKING:
    from ..coordinator import Coordinator


class MqttRuntime:
    """MQTT runtime behavior extracted from the coordinator."""

    def __init__(
        self,
        coordinator: Coordinator,
        *,
        polling_multiplier: int,
        connect_status_mqtt_stale_seconds: float,
        logger: logging.Logger,
    ) -> None:
        """Initialize extracted MQTT runtime wrapper."""
        self._coordinator = coordinator
        self._polling_multiplier = polling_multiplier
        self._connect_status_mqtt_stale_seconds = connect_status_mqtt_stale_seconds
        self._logger = logger

    def on_connect(self) -> None:
        """Handle MQTT connection."""
        coordinator = self._coordinator
        coordinator._mqtt_connected = True
        coordinator._mqtt_disconnect_time = None
        coordinator._mqtt_disconnect_notified = False
        coordinator._connect_status_skip_history.clear()

        base = coordinator._base_scan_interval
        relaxed = resolve_polling_interval_seconds_on_mqtt_connect(
            base_seconds=base,
            multiplier=self._polling_multiplier,
        )
        coordinator.update_interval = timedelta(seconds=relaxed)
        self._logger.info(
            "MQTT connected, polling interval relaxed to %ds",
            relaxed,
        )

    def on_disconnect(self) -> None:
        """Handle MQTT disconnection."""
        coordinator = self._coordinator
        coordinator._mqtt_connected = False
        coordinator._mqtt_disconnect_time = resolve_disconnect_started_at(
            coordinator._mqtt_disconnect_time,
            now=monotonic(),
        )
        coordinator._connect_status_skip_history.clear()
        coordinator._connect_status_mqtt_stale_seconds = (
            self._connect_status_mqtt_stale_seconds
        )
        coordinator._force_connect_status_refresh = True

        base = coordinator._base_scan_interval
        restored = resolve_polling_interval_seconds_on_mqtt_disconnect(
            base_seconds=base
        )
        coordinator.update_interval = timedelta(seconds=restored)
        self._logger.warning(
            "MQTT disconnected, polling interval restored to %ds",
            base,
        )

    def check_disconnect_notification(self) -> None:
        """Send persistent notification if MQTT has been disconnected too long."""
        coordinator = self._coordinator
        minutes = resolve_disconnect_notification_minutes(
            mqtt_enabled=coordinator._mqtt_enabled,
            mqtt_connected=coordinator._mqtt_connected,
            disconnect_started_at=coordinator._mqtt_disconnect_time,
            disconnect_notified=coordinator._mqtt_disconnect_notified,
            now=monotonic(),
            threshold_seconds=MQTT_DISCONNECT_NOTIFY_THRESHOLD,
        )
        if minutes is None:
            return

        coordinator._mqtt_disconnect_notified = True
        coordinator._track_background_task(
            coordinator._async_show_mqtt_disconnect_notification(minutes)
        )
