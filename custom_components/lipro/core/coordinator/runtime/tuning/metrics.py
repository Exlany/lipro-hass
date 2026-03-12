"""Metrics collection for adaptive tuning decisions."""

from __future__ import annotations

from collections import deque
import logging
from time import monotonic
from typing import TypedDict

_LOGGER = logging.getLogger(__name__)


class BatchMetric(TypedDict):
    """One recorded batch query metric sample."""

    batch_size: int
    duration: float
    device_count: int
    fallback_depth: int


class UserActionMetric(TypedDict):
    """One recorded user command action."""

    device_serial: str
    command: str
    timestamp: float


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
        self._batch_metrics: deque[BatchMetric] = deque(maxlen=metrics_window)
        self._connect_status_skip_history: deque[bool] = deque(maxlen=20)
        self._user_actions: deque[UserActionMetric] = deque(maxlen=metrics_window)

    def record_batch_metric(
        self,
        *,
        batch_size: int,
        duration: float,
        device_count: int,
        fallback_depth: int = 0,
    ) -> None:
        """Record a batch query metric."""
        metric: BatchMetric = {
            "batch_size": int(batch_size),
            "duration": float(duration),
            "device_count": int(device_count),
            "fallback_depth": int(fallback_depth),
        }
        self._batch_metrics.append(metric)

    def record_user_action(
        self,
        *,
        device_serial: str,
        command: str,
    ) -> None:
        """Record a user command action for learning curve analysis."""
        self._user_actions.append(
            UserActionMetric(
                device_serial=device_serial,
                command=command,
                timestamp=monotonic(),
            )
        )

    def get_user_action_count(self) -> int:
        """Get total number of recorded user actions."""
        return len(self._user_actions)

    def record_connect_status_skip(self, skipped: bool) -> None:
        """Record whether a connect status query was skipped."""
        self._connect_status_skip_history.append(skipped)

    def get_average_latency(self) -> float | None:
        """Get average batch query latency from recent samples."""
        if not self._batch_metrics:
            return None

        recent = list(self._batch_metrics)[-self._sample_size :]
        if not recent:
            return None

        total_duration = sum((m["duration"] for m in recent), 0.0)
        return total_duration / len(recent)

    def get_average_batch_size(self) -> float | None:
        """Get average batch size from recent samples."""
        if not self._batch_metrics:
            return None

        recent = list(self._batch_metrics)[-self._sample_size :]
        if not recent:
            return None

        total_size = sum((m["batch_size"] for m in recent), 0)
        return total_size / len(recent)

    def get_connect_status_skip_ratio(self) -> float | None:
        """Get ratio of skipped connect status queries."""
        if not self._connect_status_skip_history:
            return None

        skipped_count = sum(1 for skipped in self._connect_status_skip_history if skipped)
        return skipped_count / len(self._connect_status_skip_history)

    def get_metrics_summary(self) -> dict[str, object]:
        """Get summary of collected metrics."""
        avg_latency = self.get_average_latency()
        avg_batch_size = self.get_average_batch_size()
        skip_ratio = self.get_connect_status_skip_ratio()

        return {
            "sample_count": len(self._batch_metrics),
            "avg_latency": avg_latency,
            "avg_batch_size": avg_batch_size,
            "skip_ratio": skip_ratio,
            "user_action_count": len(self._user_actions),
            "metrics_window": self._metrics_window,
            "sample_size": self._sample_size,
        }

    def clear_metrics(self) -> None:
        """Clear all collected metrics."""
        self._batch_metrics.clear()
        self._connect_status_skip_history.clear()
        self._user_actions.clear()


__all__ = ["TuningMetrics"]
