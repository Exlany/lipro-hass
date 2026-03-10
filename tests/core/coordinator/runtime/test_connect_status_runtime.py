"""Tests for connect-status runtime tuning helpers."""

from __future__ import annotations

import pytest

from custom_components.lipro.core.coordinator.runtime.connect_status_runtime import (
    adapt_connect_status_stale_window,
    resolve_connect_status_query_interval_seconds,
)


class TestResolveConnectStatusQueryIntervalSeconds:
    """Test resolve_connect_status_query_interval_seconds."""

    def test_mqtt_disabled_returns_normal(self) -> None:
        """Test returns normal interval when MQTT disabled."""
        result = resolve_connect_status_query_interval_seconds(
            mqtt_enabled=False,
            mqtt_connected=False,
            mqtt_disconnect_time=None,
            backoff_allows_attempt=True,
            normal_interval_seconds=60.0,
            degraded_interval_seconds=300.0,
        )
        assert result == 60.0

    def test_mqtt_connected_returns_normal(self) -> None:
        """Test returns normal interval when MQTT connected."""
        result = resolve_connect_status_query_interval_seconds(
            mqtt_enabled=True,
            mqtt_connected=True,
            mqtt_disconnect_time=None,
            backoff_allows_attempt=True,
            normal_interval_seconds=60.0,
            degraded_interval_seconds=300.0,
        )
        assert result == 60.0

    def test_mqtt_disconnected_with_time_returns_degraded(self) -> None:
        """Test returns degraded interval when MQTT disconnected with time."""
        result = resolve_connect_status_query_interval_seconds(
            mqtt_enabled=True,
            mqtt_connected=False,
            mqtt_disconnect_time=1234567890.0,
            backoff_allows_attempt=True,
            normal_interval_seconds=60.0,
            degraded_interval_seconds=300.0,
        )
        assert result == 300.0

    def test_mqtt_disconnected_backoff_blocked_returns_degraded(self) -> None:
        """Test returns degraded interval when backoff blocks attempt."""
        result = resolve_connect_status_query_interval_seconds(
            mqtt_enabled=True,
            mqtt_connected=False,
            mqtt_disconnect_time=None,
            backoff_allows_attempt=False,
            normal_interval_seconds=60.0,
            degraded_interval_seconds=300.0,
        )
        assert result == 300.0

    def test_mqtt_disconnected_backoff_allows_returns_normal(self) -> None:
        """Test returns normal interval when backoff allows and no disconnect time."""
        result = resolve_connect_status_query_interval_seconds(
            mqtt_enabled=True,
            mqtt_connected=False,
            mqtt_disconnect_time=None,
            backoff_allows_attempt=True,
            normal_interval_seconds=60.0,
            degraded_interval_seconds=300.0,
        )
        assert result == 60.0


class TestAdaptConnectStatusStaleWindow:
    """Test adapt_connect_status_stale_window."""

    def test_insufficient_history_returns_current(self) -> None:
        """Test returns current value when history too short."""
        result = adapt_connect_status_stale_window(
            history=[True, False],
            current_stale_seconds=120.0,
            window_size=5,
            skip_ratio_low=0.2,
            skip_ratio_high=0.8,
            adjust_step_seconds=10.0,
            min_stale_seconds=60.0,
            max_stale_seconds=300.0,
        )
        assert result == 120.0

    def test_low_skip_ratio_increases_window(self) -> None:
        """Test increases window when skip ratio is low."""
        result = adapt_connect_status_stale_window(
            history=[False, False, False, False, False],  # 0% skip
            current_stale_seconds=120.0,
            window_size=5,
            skip_ratio_low=0.2,
            skip_ratio_high=0.8,
            adjust_step_seconds=10.0,
            min_stale_seconds=60.0,
            max_stale_seconds=300.0,
        )
        assert result == 130.0

    def test_high_skip_ratio_decreases_window(self) -> None:
        """Test decreases window when skip ratio is high."""
        result = adapt_connect_status_stale_window(
            history=[True, True, True, True, True],  # 100% skip
            current_stale_seconds=120.0,
            window_size=5,
            skip_ratio_low=0.2,
            skip_ratio_high=0.8,
            adjust_step_seconds=10.0,
            min_stale_seconds=60.0,
            max_stale_seconds=300.0,
        )
        assert result == 110.0

    def test_medium_skip_ratio_no_change(self) -> None:
        """Test no change when skip ratio in middle range."""
        result = adapt_connect_status_stale_window(
            history=[True, False, True, False, False],  # 40% skip
            current_stale_seconds=120.0,
            window_size=5,
            skip_ratio_low=0.2,
            skip_ratio_high=0.8,
            adjust_step_seconds=10.0,
            min_stale_seconds=60.0,
            max_stale_seconds=300.0,
        )
        assert result == 120.0

    def test_clamps_to_max(self) -> None:
        """Test clamps to maximum stale seconds."""
        result = adapt_connect_status_stale_window(
            history=[False, False, False, False, False],
            current_stale_seconds=295.0,
            window_size=5,
            skip_ratio_low=0.2,
            skip_ratio_high=0.8,
            adjust_step_seconds=10.0,
            min_stale_seconds=60.0,
            max_stale_seconds=300.0,
        )
        assert result == 300.0

    def test_clamps_to_min(self) -> None:
        """Test clamps to minimum stale seconds."""
        result = adapt_connect_status_stale_window(
            history=[True, True, True, True, True],
            current_stale_seconds=65.0,
            window_size=5,
            skip_ratio_low=0.2,
            skip_ratio_high=0.8,
            adjust_step_seconds=10.0,
            min_stale_seconds=60.0,
            max_stale_seconds=300.0,
        )
        assert result == 60.0

    def test_exact_window_size(self) -> None:
        """Test with history exactly matching window size."""
        result = adapt_connect_status_stale_window(
            history=[True, False, False, False, False],  # 20% skip (at threshold)
            current_stale_seconds=120.0,
            window_size=5,
            skip_ratio_low=0.2,
            skip_ratio_high=0.8,
            adjust_step_seconds=10.0,
            min_stale_seconds=60.0,
            max_stale_seconds=300.0,
        )
        # At exact threshold, should not change
        assert result == 120.0

    def test_larger_history_than_window(self) -> None:
        """Test with history larger than window size."""
        result = adapt_connect_status_stale_window(
            history=[False, False, False, False, False, False, False],  # 0% skip
            current_stale_seconds=120.0,
            window_size=5,
            skip_ratio_low=0.2,
            skip_ratio_high=0.8,
            adjust_step_seconds=10.0,
            min_stale_seconds=60.0,
            max_stale_seconds=300.0,
        )
        # Uses all history, not just window_size
        assert result == 130.0
