"""Adaptive tuning algorithms for batch size decisions."""

from __future__ import annotations

from typing import Any


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
        """Store the latency thresholds and batch bounds for tuning."""
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
        """Compute the next batch size from current latency observations."""
        if avg_latency < self._latency_low_threshold:
            new_size = current_size + self._batch_adjust_step
        elif avg_latency > self._latency_high_threshold:
            new_size = current_size - self._batch_adjust_step
        else:
            new_size = current_size
        return max(self._batch_size_min, min(new_size, self._batch_size_max))

    def get_algorithm_config(self) -> dict[str, Any]:
        """Return a serializable snapshot of algorithm thresholds and bounds."""
        return {
            "batch_size_min": self._batch_size_min,
            "batch_size_max": self._batch_size_max,
            "batch_adjust_step": self._batch_adjust_step,
            "latency_low_threshold": self._latency_low_threshold,
            "latency_high_threshold": self._latency_high_threshold,
        }


__all__ = ["TuningAlgorithm"]
