"""Adaptive tuning algorithms for batch size and polling intervals."""

from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class TuningAlgorithm:
    """Adaptive algorithms for runtime parameter tuning."""

    def __init__(
        self,
        *,
        batch_size_min: int,
        batch_size_max: int,
        batch_adjust_step: int,
        latency_low_threshold: float,
        latency_high_threshold: float,
    ) -> None:
        """Initialize tuning algorithm.

        Args:
            batch_size_min: Minimum batch size
            batch_size_max: Maximum batch size
            batch_adjust_step: Step size for batch adjustments
            latency_low_threshold: Low latency threshold in seconds
            latency_high_threshold: High latency threshold in seconds
        """
        self._batch_size_min = batch_size_min
        self._batch_size_max = batch_size_max
        self._batch_adjust_step = batch_adjust_step
        self._latency_low_threshold = latency_low_threshold
        self._latency_high_threshold = latency_high_threshold

    def compute_adaptive_batch_size(
        self,
        current_size: int,
        avg_latency: float,
    ) -> int:
        """Compute adaptive batch size based on latency metrics.

        Args:
            current_size: Current batch size
            avg_latency: Average query latency in seconds

        Returns:
            New batch size within configured bounds
        """
        if avg_latency < self._latency_low_threshold:
            # Low latency: increase batch size
            new_size = current_size + self._batch_adjust_step
        elif avg_latency > self._latency_high_threshold:
            # High latency: decrease batch size
            new_size = current_size - self._batch_adjust_step
        else:
            # Acceptable latency: keep current size
            new_size = current_size

        # Clamp to bounds
        new_size = max(self._batch_size_min, min(new_size, self._batch_size_max))

        if new_size != current_size:
            _LOGGER.debug(
                "Adaptive batch size: %d -> %d (latency: %.2fs)",
                current_size,
                new_size,
                avg_latency,
            )

        return new_size

    def compute_connect_status_interval(
        self,
        *,
        mqtt_connected: bool,
        base_interval: float,
        degraded_interval: float,
    ) -> float:
        """Compute connect status query interval based on MQTT state.

        Args:
            mqtt_connected: Whether MQTT is connected
            base_interval: Normal interval in seconds
            degraded_interval: Degraded interval when MQTT is down

        Returns:
            Query interval in seconds
        """
        return base_interval if mqtt_connected else degraded_interval

    def compute_mqtt_stale_window(
        self,
        skip_ratio: float,
        *,
        base_window: float,
        min_window: float,
        max_window: float,
        adjust_step: float,
    ) -> float:
        """Compute MQTT stale window based on skip ratio.

        Args:
            skip_ratio: Ratio of skipped queries (0.0-1.0)
            base_window: Base stale window in seconds
            min_window: Minimum window in seconds
            max_window: Maximum window in seconds
            adjust_step: Adjustment step in seconds

        Returns:
            Adjusted stale window in seconds
        """
        if skip_ratio < 0.20:
            # Low skip ratio: MQTT is unreliable, reduce window
            new_window = base_window - adjust_step
        elif skip_ratio > 0.85:
            # High skip ratio: MQTT is reliable, increase window
            new_window = base_window + adjust_step
        else:
            # Acceptable skip ratio: keep current window
            new_window = base_window

        # Clamp to bounds
        return max(min_window, min(new_window, max_window))

    def get_algorithm_config(self) -> dict[str, Any]:
        """Get algorithm configuration.

        Returns:
            Dictionary with algorithm parameters
        """
        return {
            "batch_size_min": self._batch_size_min,
            "batch_size_max": self._batch_size_max,
            "batch_adjust_step": self._batch_adjust_step,
            "latency_low_threshold": self._latency_low_threshold,
            "latency_high_threshold": self._latency_high_threshold,
        }


__all__ = ["TuningAlgorithm"]
