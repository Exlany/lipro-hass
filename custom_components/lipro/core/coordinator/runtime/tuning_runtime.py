"""Tuning runtime implementation with dependency injection."""

from __future__ import annotations

import logging

from ..types import RuntimeMetrics
from .tuning import TuningAdjuster, TuningAlgorithm, TuningMetrics

_LOGGER = logging.getLogger(__name__)


class TuningRuntime:
    """Standalone adaptive tuning runtime with no coordinator dependency."""

    def __init__(
        self,
        *,
        batch_size_min: int = 16,
        batch_size_max: int = 64,
        batch_adjust_step: int = 8,
        latency_low_threshold: float = 1.2,
        latency_high_threshold: float = 3.5,
        metrics_window: int = 24,
        sample_size: int = 6,
        initial_batch_size: int = 32,
        initial_mqtt_stale_window: float = 180.0,
    ) -> None:
        """Initialize tuning runtime.

        Args:
            batch_size_min: Minimum batch size
            batch_size_max: Maximum batch size
            batch_adjust_step: Step size for batch adjustments
            latency_low_threshold: Low latency threshold in seconds
            latency_high_threshold: High latency threshold in seconds
            metrics_window: Maximum number of metrics to retain
            sample_size: Number of recent samples to analyze
            initial_batch_size: Initial batch size
            initial_mqtt_stale_window: Initial MQTT stale window
        """
        self._algorithm = TuningAlgorithm(
            batch_size_min=batch_size_min,
            batch_size_max=batch_size_max,
            batch_adjust_step=batch_adjust_step,
            latency_low_threshold=latency_low_threshold,
            latency_high_threshold=latency_high_threshold,
        )
        self._metrics = TuningMetrics(
            metrics_window=metrics_window,
            sample_size=sample_size,
        )
        self._adjuster = TuningAdjuster()
        self._adjuster.reset_adjustments(
            batch_size=initial_batch_size,
            mqtt_stale_window=initial_mqtt_stale_window,
        )

    # User action tracking (Phase H4: learning curves)
    def record_user_action(self, device_serial: str, command: str) -> None:
        """Record a user command action for learning curve analysis.

        Called by CoordinatorCommandService after successful command dispatch.
        Used to track user adjustment patterns (e.g. color temperature preferences).
        """
        self._metrics.record_user_action(
            device_serial=device_serial,
            command=command,
        )

    # Metrics collection
    def record_batch_metric(
        self,
        *,
        batch_size: int,
        duration: float,
        device_count: int,
        fallback_depth: int = 0,
    ) -> None:
        """Record a batch query metric."""
        self._metrics.record_batch_metric(
            batch_size=batch_size,
            duration=duration,
            device_count=device_count,
            fallback_depth=fallback_depth,
        )

    def record_connect_status_skip(self, skipped: bool) -> None:
        """Record whether a connect status query was skipped."""
        self._metrics.record_connect_status_skip(skipped)

    def get_average_latency(self) -> float | None:
        """Get average batch query latency from recent samples."""
        return self._metrics.get_average_latency()

    def get_average_batch_size(self) -> float | None:
        """Get average batch size from recent samples."""
        return self._metrics.get_average_batch_size()

    def get_connect_status_skip_ratio(self) -> float | None:
        """Get ratio of skipped connect status queries."""
        return self._metrics.get_connect_status_skip_ratio()

    # Algorithm decisions
    def compute_adaptive_batch_size(self) -> int | None:
        """Compute adaptive batch size based on collected metrics.

        Returns:
            New batch size, or None if insufficient data
        """
        avg_latency = self._metrics.get_average_latency()
        if avg_latency is None:
            return None

        current_size = self._adjuster.get_current_batch_size()
        return self._algorithm.compute_adaptive_batch_size(current_size, avg_latency)

    def compute_connect_status_interval(
        self,
        *,
        mqtt_connected: bool,
        base_interval: float,
        degraded_interval: float,
    ) -> float:
        """Compute connect status query interval based on MQTT state."""
        return self._algorithm.compute_connect_status_interval(
            mqtt_connected=mqtt_connected,
            base_interval=base_interval,
            degraded_interval=degraded_interval,
        )

    def compute_mqtt_stale_window(
        self,
        *,
        base_window: float,
        min_window: float,
        max_window: float,
        adjust_step: float,
    ) -> float | None:
        """Compute MQTT stale window based on skip ratio.

        Returns:
            New stale window, or None if insufficient data
        """
        skip_ratio = self._metrics.get_connect_status_skip_ratio()
        if skip_ratio is None:
            return None

        return self._algorithm.compute_mqtt_stale_window(
            skip_ratio,
            base_window=base_window,
            min_window=min_window,
            max_window=max_window,
            adjust_step=adjust_step,
        )

    # Apply adjustments
    def apply_batch_size_adjustment(self, new_size: int) -> bool:
        """Apply batch size adjustment."""
        return self._adjuster.apply_batch_size_adjustment(new_size)

    def apply_mqtt_stale_window_adjustment(self, new_window: float) -> bool:
        """Apply MQTT stale window adjustment."""
        return self._adjuster.apply_mqtt_stale_window_adjustment(new_window)

    def get_current_batch_size(self) -> int:
        """Get current batch size."""
        return self._adjuster.get_current_batch_size()

    def get_current_mqtt_stale_window(self) -> float:
        """Get current MQTT stale window."""
        return self._adjuster.get_current_mqtt_stale_window()

    # State management
    def clear_metrics(self) -> None:
        """Clear all collected metrics."""
        self._metrics.clear_metrics()

    def reset_adjustments(self, *, batch_size: int, mqtt_stale_window: float) -> None:
        """Reset to initial values."""
        self._adjuster.reset_adjustments(
            batch_size=batch_size,
            mqtt_stale_window=mqtt_stale_window,
        )

    def get_runtime_metrics(self) -> RuntimeMetrics:
        """Get combined runtime metrics."""
        return {
            "algorithm": self._algorithm.get_algorithm_config(),
            "metrics": self._metrics.get_metrics_summary(),
            "adjuster": self._adjuster.get_adjuster_state(),
        }


__all__ = ["TuningRuntime"]
