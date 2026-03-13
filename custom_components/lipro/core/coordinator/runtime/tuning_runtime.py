"""Tuning runtime implementation with dependency injection."""

from __future__ import annotations

from ..types import RuntimeMetrics
from .tuning import TuningAdjuster, TuningAlgorithm, TuningMetrics


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
    ) -> None:
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
        self._adjuster.reset_adjustments(batch_size=initial_batch_size)

    def record_user_action(self, device_serial: str, command: str) -> None:
        self._metrics.record_user_action(device_serial=device_serial, command=command)

    def record_batch_metric(
        self,
        *,
        batch_size: int,
        duration: float,
        device_count: int,
        fallback_depth: int = 0,
    ) -> None:
        self._metrics.record_batch_metric(
            batch_size=batch_size,
            duration=duration,
            device_count=device_count,
            fallback_depth=fallback_depth,
        )

    def get_average_latency(self) -> float | None:
        return self._metrics.get_average_latency()

    def get_average_batch_size(self) -> float | None:
        return self._metrics.get_average_batch_size()

    def compute_adaptive_batch_size(self) -> int | None:
        avg_latency = self._metrics.get_average_latency()
        if avg_latency is None:
            return None
        return self._algorithm.compute_adaptive_batch_size(
            self._adjuster.get_current_batch_size(),
            avg_latency,
        )

    def apply_batch_size_adjustment(self, new_size: int) -> bool:
        return self._adjuster.apply_batch_size_adjustment(new_size)

    def get_current_batch_size(self) -> int:
        return self._adjuster.get_current_batch_size()

    def clear_metrics(self) -> None:
        self._metrics.clear_metrics()

    def reset_adjustments(self, *, batch_size: int) -> None:
        self._adjuster.reset_adjustments(batch_size=batch_size)

    def get_runtime_metrics(self) -> RuntimeMetrics:
        return {
            "algorithm": self._algorithm.get_algorithm_config(),
            "metrics": self._metrics.get_metrics_summary(),
            "adjuster": self._adjuster.get_adjuster_state(),
        }


__all__ = ["TuningRuntime"]
