"""Pure connect-status runtime tuning helpers."""

from __future__ import annotations

from collections.abc import Sequence


def resolve_connect_status_query_interval_seconds(
    *,
    mqtt_enabled: bool,
    mqtt_connected: bool,
    mqtt_disconnect_time: float | None,
    backoff_allows_attempt: bool,
    normal_interval_seconds: float,
    degraded_interval_seconds: float,
) -> float:
    """Resolve connect-status polling interval with MQTT degradation fallback."""
    if not mqtt_enabled:
        return normal_interval_seconds
    if mqtt_connected:
        return normal_interval_seconds
    if mqtt_disconnect_time is not None:
        return degraded_interval_seconds
    if not backoff_allows_attempt:
        return degraded_interval_seconds
    return normal_interval_seconds


def adapt_connect_status_stale_window(
    *,
    history: Sequence[bool],
    current_stale_seconds: float,
    window_size: int,
    skip_ratio_low: float,
    skip_ratio_high: float,
    adjust_step_seconds: float,
    min_stale_seconds: float,
    max_stale_seconds: float,
) -> float:
    """Adapt MQTT stale window based on recent connect skip ratio."""
    if len(history) < window_size:
        return current_stale_seconds

    skip_ratio = sum(history) / len(history)
    updated = current_stale_seconds
    if skip_ratio < skip_ratio_low:
        updated = min(max_stale_seconds, current_stale_seconds + adjust_step_seconds)
    elif skip_ratio > skip_ratio_high:
        updated = max(min_stale_seconds, current_stale_seconds - adjust_step_seconds)
    return updated
