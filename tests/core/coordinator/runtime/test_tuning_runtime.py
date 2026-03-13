"""Tests for TuningRuntime."""

from __future__ import annotations

import pytest

from custom_components.lipro.core.coordinator.runtime.tuning_runtime import (
    TuningRuntime,
)


@pytest.fixture
def tuning_runtime() -> TuningRuntime:
    return TuningRuntime(
        batch_size_min=16,
        batch_size_max=64,
        batch_adjust_step=8,
        latency_low_threshold=1.2,
        latency_high_threshold=3.5,
        metrics_window=24,
        sample_size=6,
        initial_batch_size=32,
    )


class TestTuningMetrics:
    def test_record_batch_metric(self, tuning_runtime: TuningRuntime) -> None:
        tuning_runtime.record_batch_metric(
            batch_size=32,
            duration=2.0,
            device_count=30,
            fallback_depth=0,
        )
        assert tuning_runtime.get_average_latency() == 2.0

    def test_record_multiple_batch_metrics(self, tuning_runtime: TuningRuntime) -> None:
        for i in range(10):
            tuning_runtime.record_batch_metric(
                batch_size=32,
                duration=1.0 + i * 0.1,
                device_count=30,
            )
        avg_latency = tuning_runtime.get_average_latency()
        assert avg_latency is not None
        assert avg_latency > 1.0

    def test_get_average_latency_no_data(self, tuning_runtime: TuningRuntime) -> None:
        assert tuning_runtime.get_average_latency() is None

    def test_get_average_batch_size(self, tuning_runtime: TuningRuntime) -> None:
        tuning_runtime.record_batch_metric(batch_size=32, duration=1.0, device_count=30)
        tuning_runtime.record_batch_metric(batch_size=40, duration=1.0, device_count=30)
        assert tuning_runtime.get_average_batch_size() == 36.0

    def test_clear_metrics(self, tuning_runtime: TuningRuntime) -> None:
        tuning_runtime.record_batch_metric(batch_size=32, duration=1.0, device_count=30)
        tuning_runtime.clear_metrics()
        assert tuning_runtime.get_average_latency() is None


class TestTuningAlgorithm:
    def test_compute_adaptive_batch_size_increase(self, tuning_runtime: TuningRuntime) -> None:
        for _ in range(6):
            tuning_runtime.record_batch_metric(batch_size=32, duration=1.0, device_count=30)
        assert tuning_runtime.compute_adaptive_batch_size() == 40

    def test_compute_adaptive_batch_size_decrease(self, tuning_runtime: TuningRuntime) -> None:
        for _ in range(6):
            tuning_runtime.record_batch_metric(batch_size=32, duration=4.0, device_count=30)
        assert tuning_runtime.compute_adaptive_batch_size() == 24

    def test_compute_adaptive_batch_size_no_change(self, tuning_runtime: TuningRuntime) -> None:
        for _ in range(6):
            tuning_runtime.record_batch_metric(batch_size=32, duration=2.0, device_count=30)
        assert tuning_runtime.compute_adaptive_batch_size() == 32

    def test_compute_adaptive_batch_size_min_bound(self, tuning_runtime: TuningRuntime) -> None:
        tuning_runtime.apply_batch_size_adjustment(16)
        for _ in range(6):
            tuning_runtime.record_batch_metric(batch_size=16, duration=4.0, device_count=15)
        assert tuning_runtime.compute_adaptive_batch_size() == 16

    def test_compute_adaptive_batch_size_max_bound(self, tuning_runtime: TuningRuntime) -> None:
        tuning_runtime.apply_batch_size_adjustment(64)
        for _ in range(6):
            tuning_runtime.record_batch_metric(batch_size=64, duration=1.0, device_count=60)
        assert tuning_runtime.compute_adaptive_batch_size() == 64

    def test_compute_adaptive_batch_size_insufficient_data(self, tuning_runtime: TuningRuntime) -> None:
        assert tuning_runtime.compute_adaptive_batch_size() is None


class TestTuningAdjuster:
    def test_apply_batch_size_adjustment(self, tuning_runtime: TuningRuntime) -> None:
        assert tuning_runtime.apply_batch_size_adjustment(40) is True
        assert tuning_runtime.get_current_batch_size() == 40

    def test_apply_batch_size_adjustment_no_change(self, tuning_runtime: TuningRuntime) -> None:
        assert tuning_runtime.apply_batch_size_adjustment(32) is False

    def test_reset_adjustments(self, tuning_runtime: TuningRuntime) -> None:
        tuning_runtime.apply_batch_size_adjustment(40)
        tuning_runtime.reset_adjustments(batch_size=32)
        assert tuning_runtime.get_current_batch_size() == 32

    def test_get_runtime_metrics(self, tuning_runtime: TuningRuntime) -> None:
        metrics = tuning_runtime.get_runtime_metrics()
        assert "algorithm" in metrics
        assert "metrics" in metrics
        assert "adjuster" in metrics
