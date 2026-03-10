"""Tests for connect-status runtime tuning helpers."""

from __future__ import annotations

import pytest

from custom_components.lipro.core.coordinator.runtime.connect_status_runtime import (
    adapt_connect_status_stale_window,
    resolve_connect_status_query_interval_seconds,
)


@pytest.mark.parametrize(
    (
        "mqtt_enabled",
        "mqtt_connected",
        "mqtt_disconnect_time",
        "backoff_allows_attempt",
        "expected",
    ),
    [
        (False, False, None, True, 60.0),
        (True, True, None, True, 60.0),
        (True, False, 1234567890.0, True, 300.0),
        (True, False, None, False, 300.0),
        (True, False, None, True, 60.0),
    ],
)
def test_resolve_connect_status_query_interval_seconds(
    mqtt_enabled: bool,
    mqtt_connected: bool,
    mqtt_disconnect_time: float | None,
    backoff_allows_attempt: bool,
    expected: float,
) -> None:
    """Polling interval should degrade only for disconnected MQTT states."""
    assert (
        resolve_connect_status_query_interval_seconds(
            mqtt_enabled=mqtt_enabled,
            mqtt_connected=mqtt_connected,
            mqtt_disconnect_time=mqtt_disconnect_time,
            backoff_allows_attempt=backoff_allows_attempt,
            normal_interval_seconds=60.0,
            degraded_interval_seconds=300.0,
        )
        == expected
    )


def test_adapt_connect_status_stale_window_handles_short_history() -> None:
    """Insufficient history should leave the stale window unchanged."""
    assert (
        adapt_connect_status_stale_window(
            history=[True, False],
            current_stale_seconds=120.0,
            window_size=5,
            skip_ratio_low=0.2,
            skip_ratio_high=0.8,
            adjust_step_seconds=10.0,
            min_stale_seconds=60.0,
            max_stale_seconds=300.0,
        )
        == 120.0
    )


@pytest.mark.parametrize(
    ("history", "current", "expected"),
    [
        ([False, False, False, False, False], 120.0, 130.0),
        ([True, True, True, True, True], 120.0, 110.0),
        ([True, False, True, False, False], 120.0, 120.0),
        ([False, False, False, False, False], 295.0, 300.0),
        ([True, True, True, True, True], 65.0, 60.0),
    ],
)
def test_adapt_connect_status_stale_window_adjusts_and_clamps(
    history: list[bool],
    current: float,
    expected: float,
) -> None:
    """Skip ratio should widen, shrink, or clamp the stale threshold."""
    assert (
        adapt_connect_status_stale_window(
            history=history,
            current_stale_seconds=current,
            window_size=5,
            skip_ratio_low=0.2,
            skip_ratio_high=0.8,
            adjust_step_seconds=10.0,
            min_stale_seconds=60.0,
            max_stale_seconds=300.0,
        )
        == expected
    )
