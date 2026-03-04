"""Tests for pure connect-status and state-batch strategy helpers."""

from __future__ import annotations

from custom_components.lipro.core.coordinator.runtime.status_strategy import (
    _is_mqtt_connect_stale,
    compute_adaptive_state_batch_size,
    resolve_connect_status_query_candidates,
)


def _normalize(device_id: str) -> str:
    return device_id.strip().lower()


def test_resolve_empty_iot_ids_returns_empty_decision() -> None:
    decision = resolve_connect_status_query_candidates(
        iot_ids=[],
        force_refresh=False,
        mqtt_enabled=True,
        mqtt_connected=True,
        last_query_time=0.0,
        now=100.0,
        priority_ids=set(),
        mqtt_recent_time_by_id={},
        stale_window_seconds=60.0,
        query_interval_seconds=10.0,
        normalize=_normalize,
    )
    assert decision.query_ids == []
    assert decision.record_skip is None


def test_resolve_deduplicates_priority_and_stale_overlap() -> None:
    decision = resolve_connect_status_query_candidates(
        iot_ids=["dev1"],
        force_refresh=False,
        mqtt_enabled=True,
        mqtt_connected=True,
        last_query_time=0.0,
        now=200.0,
        priority_ids={"dev1"},
        mqtt_recent_time_by_id={"dev1": 0.0},
        stale_window_seconds=60.0,
        query_interval_seconds=10.0,
        normalize=_normalize,
    )
    assert decision.query_ids == ["dev1"]
    assert decision.query_ids.count("dev1") == 1


def test_compute_adaptive_batch_size_no_metrics_returns_current() -> None:
    result = compute_adaptive_state_batch_size(
        current_batch_size=32,
        recent_metrics=[],
        batch_size_min=16,
        batch_size_max=64,
        batch_adjust_step=8,
        metrics_sample_size=6,
        latency_low_seconds=1.2,
        latency_high_seconds=3.5,
    )
    assert result == 32


def test_is_mqtt_connect_stale_sentinel_zero() -> None:
    assert _is_mqtt_connect_stale(0.0, stale_before=50.0) is True
    assert _is_mqtt_connect_stale(-1.0, stale_before=50.0) is True


def test_is_mqtt_connect_stale_normal_comparison() -> None:
    assert _is_mqtt_connect_stale(40.0, stale_before=50.0) is True
    assert _is_mqtt_connect_stale(100.0, stale_before=50.0) is False


def test_is_mqtt_connect_stale_sentinel_with_negative_threshold() -> None:
    """Reproduces CI failure: monotonic() < stale_window on fresh containers."""
    assert _is_mqtt_connect_stale(0.0, stale_before=-130.0) is True
