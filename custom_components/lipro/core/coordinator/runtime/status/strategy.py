"""Status polling strategy for determining query targets and batching."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ....device import LiproDevice

_LOGGER = logging.getLogger(__name__)


class StatusStrategy:
    """Determine status polling strategy and query targets."""

    def __init__(
        self,
        *,
        max_devices_per_query: int,
        state_batch_size: int,
    ) -> None:
        """Initialize status strategy.

        Args:
            max_devices_per_query: Maximum devices per API query
            state_batch_size: Adaptive batch size for state queries
        """
        self._max_devices_per_query = max_devices_per_query
        self._state_batch_size = state_batch_size

    def compute_query_batches(
        self,
        device_ids: list[str],
    ) -> list[list[str]]:
        """Split device IDs into query batches.

        Args:
            device_ids: List of device IDs to query

        Returns:
            List of batches, each within max_devices_per_query limit
        """
        if not device_ids:
            return []

        batches: list[list[str]] = []
        batch_size = min(self._state_batch_size, self._max_devices_per_query)

        for i in range(0, len(device_ids), batch_size):
            batches.append(device_ids[i : i + batch_size])

        return batches

    def should_query_device(
        self,
        device: LiproDevice,
        *,
        mqtt_connected: bool,
    ) -> bool:
        """Determine if a device should be queried via REST.

        Args:
            device: Device to check
            mqtt_connected: Whether MQTT is currently connected

        Returns:
            True if device should be queried
        """
        # Always query if MQTT is disconnected
        if not mqtt_connected:
            return True

        # Query offline devices to detect reconnection
        if not device.is_online:
            return True

        # Query devices without recent MQTT updates
        if not device.has_recent_mqtt_update():
            return True

        return False

    def filter_query_candidates(
        self,
        devices: dict[str, LiproDevice],
        device_ids: list[str],
        *,
        mqtt_connected: bool,
    ) -> list[str]:
        """Filter device IDs to those needing REST queries.

        Args:
            devices: Device dictionary
            device_ids: Candidate device IDs
            mqtt_connected: Whether MQTT is connected

        Returns:
            Filtered list of device IDs to query
        """
        query_ids: list[str] = []

        for device_id in device_ids:
            device = devices.get(device_id)
            if device is None:
                continue

            if self.should_query_device(device, mqtt_connected=mqtt_connected):
                query_ids.append(device_id)

        return query_ids

    def get_current_batch_size(self) -> int:
        """Get current adaptive batch size.

        Returns:
            Current batch size
        """
        return self._state_batch_size

    def update_batch_size(self, new_size: int) -> None:
        """Update adaptive batch size.

        Args:
            new_size: New batch size to use
        """
        old_size = self._state_batch_size
        self._state_batch_size = new_size

        if old_size != new_size:
            _LOGGER.debug(
                "Updated state batch size: %d -> %d",
                old_size,
                new_size,
            )

    def get_strategy_metrics(self) -> dict[str, Any]:
        """Get current strategy metrics.

        Returns:
            Dictionary with strategy state
        """
        return {
            "max_devices_per_query": self._max_devices_per_query,
            "state_batch_size": self._state_batch_size,
        }


__all__ = ["StatusStrategy"]
