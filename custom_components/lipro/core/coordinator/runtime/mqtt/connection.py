"""MQTT connection state management."""

from __future__ import annotations

from datetime import timedelta
import logging
from time import monotonic
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


class PollingIntervalUpdater(Protocol):
    """Protocol for updating coordinator polling interval."""

    def update_polling_interval(self, interval: timedelta) -> None:
        """Update the polling interval."""
        ...


class MqttConnectionManager:
    """Manages MQTT connection state and polling interval adjustments."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        polling_updater: PollingIntervalUpdater,
        base_scan_interval: int,
        polling_multiplier: int,
        logger: logging.Logger,
    ) -> None:
        """Initialize connection manager.

        Args:
            hass: Home Assistant instance
            polling_updater: Callback to update polling interval
            base_scan_interval: Base polling interval in seconds
            polling_multiplier: Multiplier for relaxed polling when MQTT connected
            logger: Logger instance
        """
        self._hass = hass
        self._polling_updater = polling_updater
        self._base_scan_interval = base_scan_interval
        self._polling_multiplier = polling_multiplier
        self._logger = logger

        self._connected = False
        self._disconnect_time: float | None = None
        self._disconnect_notified = False

    @property
    def is_connected(self) -> bool:
        """Return current connection state."""
        return self._connected

    @property
    def disconnect_time(self) -> float | None:
        """Return disconnect timestamp if disconnected."""
        return self._disconnect_time

    @property
    def disconnect_notified(self) -> bool:
        """Return whether disconnect notification was sent."""
        return self._disconnect_notified

    def mark_disconnect_notified(self) -> None:
        """Mark that disconnect notification was sent."""
        self._disconnect_notified = True

    def on_connect(self) -> None:
        """Handle MQTT connection established."""
        self._connected = True
        self._disconnect_time = None
        self._disconnect_notified = False

        relaxed_interval = self._base_scan_interval * self._polling_multiplier
        self._polling_updater.update_polling_interval(
            timedelta(seconds=relaxed_interval)
        )
        self._logger.info(
            "MQTT connected, polling interval relaxed to %ds",
            relaxed_interval,
        )

    def on_disconnect(self) -> None:
        """Handle MQTT disconnection."""
        self._connected = False
        if self._disconnect_time is None:
            self._disconnect_time = monotonic()

        self._polling_updater.update_polling_interval(
            timedelta(seconds=self._base_scan_interval)
        )
        self._logger.warning(
            "MQTT disconnected, polling interval restored to %ds",
            self._base_scan_interval,
        )

    def reset(self) -> None:
        """Reset connection state."""
        self._connected = False
        self._disconnect_time = None
        self._disconnect_notified = False
