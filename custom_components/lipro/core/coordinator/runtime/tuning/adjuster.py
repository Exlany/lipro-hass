"""Parameter adjuster for applying tuning decisions."""

from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class TuningAdjuster:
    """Apply tuning adjustments to runtime parameters."""

    def __init__(self) -> None:
        """Initialize tuning adjuster."""
        self._current_batch_size: int = 32
        self._current_mqtt_stale_window: float = 180.0
        self._adjustment_count: int = 0

    def apply_batch_size_adjustment(self, new_size: int) -> bool:
        """Apply batch size adjustment.

        Args:
            new_size: New batch size to apply

        Returns:
            True if size changed
        """
        if new_size == self._current_batch_size:
            return False

        old_size = self._current_batch_size
        self._current_batch_size = new_size
        self._adjustment_count += 1

        _LOGGER.info(
            "Applied batch size adjustment: %d -> %d (adjustment #%d)",
            old_size,
            new_size,
            self._adjustment_count,
        )

        return True

    def apply_mqtt_stale_window_adjustment(self, new_window: float) -> bool:
        """Apply MQTT stale window adjustment.

        Args:
            new_window: New stale window in seconds

        Returns:
            True if window changed
        """
        if abs(new_window - self._current_mqtt_stale_window) < 0.1:
            return False

        old_window = self._current_mqtt_stale_window
        self._current_mqtt_stale_window = new_window
        self._adjustment_count += 1

        _LOGGER.info(
            "Applied MQTT stale window adjustment: %.1fs -> %.1fs (adjustment #%d)",
            old_window,
            new_window,
            self._adjustment_count,
        )

        return True

    def get_current_batch_size(self) -> int:
        """Get current batch size.

        Returns:
            Current batch size
        """
        return self._current_batch_size

    def get_current_mqtt_stale_window(self) -> float:
        """Get current MQTT stale window.

        Returns:
            Current stale window in seconds
        """
        return self._current_mqtt_stale_window

    def get_adjustment_count(self) -> int:
        """Get total number of adjustments made.

        Returns:
            Adjustment count
        """
        return self._adjustment_count

    def reset_adjustments(self, *, batch_size: int, mqtt_stale_window: float) -> None:
        """Reset to initial values.

        Args:
            batch_size: Initial batch size
            mqtt_stale_window: Initial MQTT stale window
        """
        self._current_batch_size = batch_size
        self._current_mqtt_stale_window = mqtt_stale_window
        self._adjustment_count = 0

        _LOGGER.debug(
            "Reset tuning adjustments: batch_size=%d, mqtt_stale_window=%.1fs",
            batch_size,
            mqtt_stale_window,
        )

    def get_adjuster_state(self) -> dict[str, Any]:
        """Get current adjuster state.

        Returns:
            Dictionary with adjuster state
        """
        return {
            "current_batch_size": self._current_batch_size,
            "current_mqtt_stale_window": self._current_mqtt_stale_window,
            "adjustment_count": self._adjustment_count,
        }


__all__ = ["TuningAdjuster"]
