"""Metrics collection for adaptive tuning decisions."""

from __future__ import annotations

from collections import deque
from time import monotonic
from typing import TypedDict


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
        self._metrics_window = metrics_window
        self._sample_size = sample_size
        self._batch_metrics: deque[BatchMetric] = deque(maxlen=metrics_window)
        self._user_actions: deque[UserActionMetric] = deque(maxlen=metrics_window)

    def record_batch_metric(
        self,
        *,
        batch_size: int,
        duration: float,
        device_count: int,
        fallback_depth: int = 0,
    ) -> None:
        self._batch_metrics.append(
            BatchMetric(
                batch_size=int(batch_size),
                duration=float(duration),
                device_count=int(device_count),
                fallback_depth=int(fallback_depth),
            )
        )

    def record_user_action(
        self,
        *,
        device_serial: str,
        command: str,
    ) -> None:
        self._user_actions.append(
            UserActionMetric(
                device_serial=device_serial,
                command=command,
                timestamp=monotonic(),
            )
        )

    def get_average_latency(self) -> float | None:
        if not self._batch_metrics:
            return None
        recent = list(self._batch_metrics)[-self._sample_size :]
        if not recent:
            return None
        total_duration = sum((metric["duration"] for metric in recent), 0.0)
        return total_duration / len(recent)

    def get_average_batch_size(self) -> float | None:
        if not self._batch_metrics:
            return None
        recent = list(self._batch_metrics)[-self._sample_size :]
        if not recent:
            return None
        total_size = sum((metric["batch_size"] for metric in recent), 0)
        return total_size / len(recent)

    def get_metrics_summary(self) -> dict[str, object]:
        return {
            "sample_count": len(self._batch_metrics),
            "avg_latency": self.get_average_latency(),
            "avg_batch_size": self.get_average_batch_size(),
            "user_action_count": len(self._user_actions),
            "metrics_window": self._metrics_window,
            "sample_size": self._sample_size,
        }

    def clear_metrics(self) -> None:
        self._batch_metrics.clear()
        self._user_actions.clear()


__all__ = ["TuningMetrics"]
