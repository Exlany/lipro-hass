"""Metrics collection for adaptive tuning decisions."""

from __future__ import annotations

from collections import deque
import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class TuningMetrics:
    """Collect and analyze metrics for adaptive tuning."""

    def __init__(
        self,
        *,
        metrics_window: int,
        sample_size: int,
    ) -> None:
        """Initialize tuning metrics.

        Args:
            metrics_window: Maximum number of metrics to retain
            sample_size: Number of recent samples to analyze
        """
        self._metrics_window = metrics_window
        self._sample_size = sample_size
        self._batch_metrics: deque[dict[str, Any]] = deque(maxlen=metrics_window)
        self._connect_status_skip_history: deque[bool] = deque(maxlen=20)

    def record_batch_metric(
        self,
        *,
        batch_size: int,
        duration: float,
        device_count: int,
        fallback_depth: int = 0,
    ) -> None:
        """Record a batch query metric.

        Args:
            batch_size: Batch size used
            duration: Query duration in seconds
            device_count: Number of devices queried
            fallback_depth: Fallback depth if applicable
        """
        self._batch_metrics.append(
            {
                "batch_size": batch_size,
                "duration": duration,
                "device_count": device_count,
                "fallback_depth": fallback_depth,
            }
        )

    def record_connect_status_skip(self, skipped: bool) -> None:
        """Record whether a connect status query was skipped.

        Args:
            skipped: True if query was skipped due to MQTT
        """
        self._connect_status_skip_history.append(skipped)

    def get_average_latency(self) -> float | None:
        """Get average batch query latency from recent samples.

        Returns:
            Average latency in seconds, or None if insufficient data
        """
        if not self._batch_metrics:
            return None

        recent = list(self._batch_metrics)[-self._sample_size :]
        if not recent:
            return None

        total_duration = sum(m["duration"] for m in recent)
        return total_duration / len(recent)

    def get_average_batch_size(self) -> float | None:
        """Get average batch size from recent samples.

        Returns:
            Average batch size, or None if insufficient data
        """
        if not self._batch_metrics:
            return None

        recent = list(self._batch_metrics)[-self._sample_size :]
        if not recent:
            return None

        total_size = sum(m["batch_size"] for m in recent)
        return total_size / len(recent)

    def get_connect_status_skip_ratio(self) -> float | None:
        """Get ratio of skipped connect status queries.

        Returns:
            Skip ratio (0.0-1.0), or None if insufficient data
        """
        if not self._connect_status_skip_history:
            return None

        skipped_count = sum(
            1 for skipped in self._connect_status_skip_history if skipped
        )
        return skipped_count / len(self._connect_status_skip_history)

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of collected metrics.

        Returns:
            Dictionary with metric summaries
        """
        avg_latency = self.get_average_latency()
        avg_batch_size = self.get_average_batch_size()
        skip_ratio = self.get_connect_status_skip_ratio()

        return {
            "sample_count": len(self._batch_metrics),
            "avg_latency": avg_latency,
            "avg_batch_size": avg_batch_size,
            "skip_ratio": skip_ratio,
            "metrics_window": self._metrics_window,
            "sample_size": self._sample_size,
        }

    def clear_metrics(self) -> None:
        """Clear all collected metrics."""
        self._batch_metrics.clear()
        self._connect_status_skip_history.clear()


__all__ = ["TuningMetrics"]
