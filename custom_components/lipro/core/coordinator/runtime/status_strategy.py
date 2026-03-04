"""Pure strategy helpers for connect-status and state-batch tuning."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass

StateBatchMetric = tuple[int, float, int]
# The coordinator may provide a normalizer that is stricter/looser than our typing;
# keep the strategy layer defensive for robustness.
NormalizeDeviceId = Callable[[str], object]


@dataclass(frozen=True)
class ConnectStatusQueryDecision:
    """Computed connect-status query decision for one refresh tick."""

    query_ids: list[str]
    next_last_query_time: float
    record_skip: bool | None


def resolve_connect_status_query_candidates(
    *,
    iot_ids: Iterable[str],
    force_refresh: bool,
    mqtt_enabled: bool,
    mqtt_connected: bool,
    last_query_time: float,
    now: float,
    priority_ids: set[str] | frozenset[str],
    mqtt_recent_time_by_id: Mapping[str, float],
    stale_window_seconds: float,
    query_interval_seconds: float,
    normalize: NormalizeDeviceId,
) -> ConnectStatusQueryDecision:
    """Resolve candidate IDs and bookkeeping for connect-status polling."""
    iot_id_list = [device_id for device_id in iot_ids if isinstance(device_id, str)]
    if not iot_id_list:
        return ConnectStatusQueryDecision(
            query_ids=[],
            next_last_query_time=last_query_time,
            record_skip=None,
        )

    next_last_query_time = last_query_time
    if force_refresh:
        next_last_query_time = now
    elif now - last_query_time < query_interval_seconds:
        return ConnectStatusQueryDecision(
            query_ids=[],
            next_last_query_time=last_query_time,
            record_skip=None,
        )
    else:
        next_last_query_time = now

    normalized_priority_ids = {
        _normalize_lookup_key(device_id, normalize) for device_id in priority_ids
    }
    priority_query_ids = [
        device_id
        for device_id in iot_id_list
        if _normalize_lookup_key(device_id, normalize) in normalized_priority_ids
    ]

    if force_refresh and priority_query_ids:
        return ConnectStatusQueryDecision(
            query_ids=priority_query_ids,
            next_last_query_time=next_last_query_time,
            record_skip=None,
        )
    if force_refresh:
        return ConnectStatusQueryDecision(
            query_ids=iot_id_list,
            next_last_query_time=next_last_query_time,
            record_skip=None,
        )

    if not (mqtt_enabled and mqtt_connected):
        return ConnectStatusQueryDecision(
            query_ids=iot_id_list,
            next_last_query_time=next_last_query_time,
            record_skip=None,
        )

    stale_before = now - stale_window_seconds
    stale_query_ids = [
        device_id
        for device_id in iot_id_list
        if _is_mqtt_connect_stale(
            mqtt_recent_time_by_id.get(
                _normalize_lookup_key(device_id, normalize), 0.0
            ),
            stale_before,
        )
    ]

    query_ids: list[str] = []
    seen_normalized_ids: set[str] = set()
    for device_id in [*priority_query_ids, *stale_query_ids]:
        normalized = _normalize_lookup_key(device_id, normalize)
        if normalized in seen_normalized_ids:
            continue
        seen_normalized_ids.add(normalized)
        query_ids.append(device_id)

    return ConnectStatusQueryDecision(
        query_ids=query_ids,
        next_last_query_time=next_last_query_time,
        record_skip=not query_ids,
    )


def compute_adaptive_state_batch_size(
    *,
    current_batch_size: int,
    recent_metrics: Sequence[StateBatchMetric],
    batch_size_min: int,
    batch_size_max: int,
    batch_adjust_step: int,
    metrics_sample_size: int,
    latency_low_seconds: float,
    latency_high_seconds: float,
    fallback_depth_threshold: int = 2,
) -> int:
    """Compute adaptive state-batch size from recent query metrics."""
    lower = max(1, batch_size_min)
    upper = max(lower, batch_size_max)
    current = _clamp(current_batch_size, lower=lower, upper=upper)

    if not recent_metrics:
        return current

    sample_size = max(1, metrics_sample_size)
    sample_count = min(sample_size, len(recent_metrics))
    recent = list(recent_metrics)[-sample_count:]
    avg_latency = sum(max(0.0, item[1]) for item in recent) / sample_count
    max_fallback_depth = max(max(0, item[2]) for item in recent)

    step = max(1, batch_adjust_step)
    updated = current
    if (
        max_fallback_depth >= fallback_depth_threshold
        or avg_latency >= latency_high_seconds
    ):
        updated = max(lower, current - step)
    elif (
        sample_count >= sample_size
        and max_fallback_depth == 0
        and avg_latency <= latency_low_seconds
    ):
        updated = min(upper, current + step)

    return updated


def _is_mqtt_connect_stale(last_time: float, stale_before: float) -> bool:
    """Return True when the device has no recent MQTT connect data.

    A ``last_time`` of ``0.0`` (or negative) is a sentinel meaning "never
    received" and is always considered stale regardless of the current clock.
    This avoids a false-fresh evaluation when ``monotonic()`` is smaller than
    the stale window (e.g. on freshly booted CI containers).
    """
    if last_time <= 0.0:
        return True
    return last_time < stale_before


def _normalize_lookup_key(device_id: str, normalize: NormalizeDeviceId) -> str:
    """Normalize one device ID using caller strategy with safe fallback."""
    try:
        normalized = normalize(device_id)
    except (TypeError, ValueError):
        normalized = device_id.strip().lower()
    if not isinstance(normalized, str):
        return device_id.strip().lower()
    return normalized


def _clamp(value: int, *, lower: int, upper: int) -> int:
    """Clamp int value to closed interval [lower, upper]."""
    return max(lower, min(upper, value))
