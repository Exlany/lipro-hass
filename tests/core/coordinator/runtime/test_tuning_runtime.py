"""Tests for TuningRuntime."""

from __future__ import annotations

import pytest

from custom_components.lipro.core.coordinator.runtime.tuning_runtime import TuningRuntime


@pytest.fixture
def tuning_runtime() -> TuningRuntime:
    """Create a TuningRuntime instance."""
    return TuningRuntime(
        batch_size_min=16,
        batch_size_max=64,
        batch_adjust_step=8,
        latency_low_threshold=1.2,
        latency_high_threshold=3.5,
        metrics_window=24,
        sample_size=6,
        initial_batch_size=32,
        initial_mqtt_stale_window=180.0,
    )


class TestTuningMetrics:
    """Test TuningMetrics functionality."""

    def test_record_batch_metric(self, tuning_runtime: TuningRuntime) -> None:
        """Test recording batch metrics."""
        tuning_runtime.record_batch_metric(
            batch_size=32,
            duration=2.0,
            device_count=30,
            fallback_depth=0,
        )
        assert tuning_runtime.get_average_latency() == 2.0

    def test_record_multiple_batch_metrics(self, tuning_runtime: TuningRuntime) -> None:
        """Test recording multiple batch metrics."""
        for i in range(10):
            tuning_runtime.record_batch_metric(
                batch_size=32,
                duration=1.0 + i * 0.1,
                device_count=30,
            )
        avg_latency = tuning_runtime.get_average_latency()
        assert avg_latency is not None
        assert avg_latency > 1.0

    def test_record_connect_status_skip(self, tuning_runtime: TuningRuntime) -> None:
        """Test recording connect status skip."""
        tuning_runtime.record_connect_status_skip(True)
        tuning_runtime.record_connect_status_skip(False)
        skip_ratio = tuning_runtime.get_connect_status_skip_ratio()
        assert skip_ratio == 0.5

    def test_get_average_latency_no_data(self, tuning_runtime: TuningRuntime) -> None:
        """Test getting average latency with no data."""
        assert tuning_runtime.get_average_latency() is None

    def test_get_average_batch_size(self, tuning_runtime: TuningRuntime) -> None:
        """Test getting average batch size."""
        tuning_runtime.record_batch_metric(batch_size=32, duration=1.0, device_count=30)
        tuning_runtime.record_batch_metric(batch_size=40, duration=1.0, device_count=30)
        avg_size = tuning_runtime.get_average_batch_size()
        assert avg_size == 36.0

    def test_clear_metrics(self, tuning_runtime: TuningRuntime) -> None:
        """Test clearing metrics."""
        tuning_runtime.record_batch_metric(batch_size=32, duration=1.0, device_count=30)
        tuning_runtime.clear_metrics()
        assert tuning_runtime.get_average_latency() is None


class TestTuningAlgorithm:
    """Test TuningAlgorithm functionality."""

    def test_compute_adaptive_batch_size_increase(self, tuning_runtime: TuningRuntime) -> None:
        """Test adaptive batch size increase on low latency."""
        for _ in range(6):
            tuning_runtime.record_batch_metric(batch_size=32, duration=1.0, device_count=30)
        new_size = tuning_runtime.compute_adaptive_batch_size()
        assert new_size == 40  # 32 + 8

    def test_compute_adaptive_batch_size_decrease(self, tuning_runtime: TuningRuntime) -> None:
        """Test adaptive batch size decrease on high latency."""
        for _ in range(6):
            tuning_runtime.record_batch_metric(batch_size=32, duration=4.0, device_count=30)
        new_size = tuning_runtime.compute_adaptive_batch_size()
        assert new_size == 24  # 32 - 8

    def test_compute_adaptive_batch_size_no_change(self, tuning_runtime: TuningRuntime) -> None:
        """Test adaptive batch size with acceptable latency."""
        for _ in range(6):
            tuning_runtime.record_batch_metric(batch_size=32, duration=2.0, device_count=30)
        new_size = tuning_runtime.compute_adaptive_batch_size()
        assert new_size == 32

    def test_compute_adaptive_batch_size_min_bound(self, tuning_runtime: TuningRuntime) -> None:
        """Test adaptive batch size respects minimum bound."""
        tuning_runtime.apply_batch_size_adjustment(16)
        for _ in range(6):
            tuning_runtime.record_batch_metric(batch_size=16, duration=4.0, device_count=15)
        new_size = tuning_runtime.compute_adaptive_batch_size()
        assert new_size == 16  # Cannot go below min

    def test_compute_adaptive_batch_size_max_bound(self, tuning_runtime: TuningRuntime) -> None:
        """Test adaptive batch size respects maximum bound."""
        tuning_runtime.apply_batch_size_adjustment(64)
        for _ in range(6):
            tuning_runtime.record_batch_metric(batch_size=64, duration=1.0, device_count=60)
        new_size = tuning_runtime.compute_adaptive_batch_size()
        assert new_size == 64  # Cannot go above max

    def test_compute_adaptive_batch_size_insufficient_data(
        self,
        tuning_runtime: TuningRuntime,
    ) -> None:
        """Test adaptive batch size with insufficient data."""
        new_size = tuning_runtime.compute_adaptive_batch_size()
        assert new_size is None

    def test_compute_connect_status_interval_mqtt_connected(
        self,
        tuning_runtime: TuningRuntime,
    ) -> None:
        """Test connect status interval when MQTT is connected."""
        interval = tuning_runtime.compute_connect_status_interval(
            mqtt_connected=True,
            base_interval=60.0,
            degraded_interval=20.0,
        )
        assert interval == 60.0

    def test_compute_connect_status_interval_mqtt_disconnected(
        self,
        tuning_runtime: TuningRuntime,
    ) -> None:
        """Test connect status interval when MQTT is disconnected."""
        interval = tuning_runtime.compute_connect_status_interval(
            mqtt_connected=False,
            base_interval=60.0,
            degraded_interval=20.0,
        )
        assert interval == 20.0

    def test_compute_mqtt_stale_window_increase(self, tuning_runtime: TuningRuntime) -> None:
        """Test MQTT stale window increase on high skip ratio."""
        for _ in range(20):
            tuning_runtime.record_connect_status_skip(True)
        new_window = tuning_runtime.compute_mqtt_stale_window(
            base_window=180.0,
            min_window=90.0,
            max_window=300.0,
            adjust_step=15.0,
        )
        assert new_window == 195.0  # 180 + 15

    def test_compute_mqtt_stale_window_decrease(self, tuning_runtime: TuningRuntime) -> None:
        """Test MQTT stale window decrease on low skip ratio."""
        for _ in range(20):
            tuning_runtime.record_connect_status_skip(False)
        new_window = tuning_runtime.compute_mqtt_stale_window(
            base_window=180.0,
            min_window=90.0,
            max_window=300.0,
            adjust_step=15.0,
        )
        assert new_window == 165.0  # 180 - 15


class TestTuningAdjuster:
    """Test TuningAdjuster functionality."""

    def test_apply_batch_size_adjustment(self, tuning_runtime: TuningRuntime) -> None:
        """Test applying batch size adjustment."""
        changed = tuning_runtime.apply_batch_size_adjustment(40)
        assert changed is True
        assert tuning_runtime.get_current_batch_size() == 40

    def test_apply_batch_size_adjustment_no_change(self, tuning_runtime: TuningRuntime) -> None:
        """Test applying batch size adjustment with no change."""
        changed = tuning_runtime.apply_batch_size_adjustment(32)
        assert changed is False

    def test_apply_mqtt_stale_window_adjustment(self, tuning_runtime: TuningRuntime) -> None:
        """Test applying MQTT stale window adjustment."""
        changed = tuning_runtime.apply_mqtt_stale_window_adjustment(200.0)
        assert changed is True
        assert tuning_runtime.get_current_mqtt_stale_window() == 200.0

    def test_apply_mqtt_stale_window_adjustment_no_change(
        self,
        tuning_runtime: TuningRuntime,
    ) -> None:
        """Test applying MQTT stale window adjustment with no change."""
        changed = tuning_runtime.apply_mqtt_stale_window_adjustment(180.0)
        assert changed is False

    def test_reset_adjustments(self, tuning_runtime: TuningRuntime) -> None:
        """Test resetting adjustments."""
        tuning_runtime.apply_batch_size_adjustment(40)
        tuning_runtime.reset_adjustments(batch_size=32, mqtt_stale_window=180.0)
        assert tuning_runtime.get_current_batch_size() == 32
        assert tuning_runtime.get_current_mqtt_stale_window() == 180.0

    def test_get_runtime_metrics(self, tuning_runtime: TuningRuntime) -> None:
        """Test getting runtime metrics."""
        metrics = tuning_runtime.get_runtime_metrics()
        assert "algorithm" in metrics
        assert "metrics" in metrics
        assert "adjuster" in metrics
        assert tuning_runtime.get_current_batch_size() == 40

    def test_apply_batch_size_adjustment_no_change(self, tuning_runtime: TuningRuntime) -> None:
        """Test applying batch size adjustment with no change."""
        changed = tuning_runtime.apply_batch_size_adjustment(32)
        assert changed is False

    def test_apply_mqtt_stale_window_adjustment(self, tuning_runtime: TuningRuntime) -> None:
        """Test applying MQTT stale window adjustment."""
        changed = tuning_runtime.apply_mqtt_stale_window_adjustment(200.0)
        assert changed is True
        assert tuning_runtime.get_current_mqtt_stale_window() == 200.0

    def test_apply_mqtt_stale_window_adjustment_no_change(
        self,
        tuning_runtime: TuningRuntime,
    ) -> None:
        """Test applying MQTT stale window adjustment with no change."""
        changed = tuning_runtime.apply_mqtt_stale_window_adjustment(180.0)
        assert changed is False

    def test_reset_adjustments(self, tuning_runtime: TuningRuntime) -> None:
        """Test resetting adjustments."""
        tuning_runtime.apply_batch_size_adjustment(40)
        tuning_runtime.reset_adjustments(batch_size=32, mqtt_stale_window=180.0)
        assert tuning_runtime.get_current_batch_size() == 32
        assert tuning_runtime.get_current_mqtt_stale_window() == 180.0

    def test_get_runtime_metrics(self, tuning_runtime: TuningRuntime) -> None:
        """Test getting runtime metrics."""
        metrics = tuning_runtime.get_runtime_metrics()
        assert "algorithm" in metrics
        assert "metrics" in metrics
        assert "adjuster" in metrics
