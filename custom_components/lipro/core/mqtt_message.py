"""MQTT message normalization and deduplication helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def is_online_connect_state(value: Any) -> bool:
    """Normalize connect-state payload variants to an online/offline boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


def compute_properties_hash(properties: dict[str, Any]) -> int | None:
    """Build stable hash for MQTT property payload deduplication.

    Returns ``None`` when payload values are not hashable.
    """
    try:
        return hash(tuple(sorted(properties.items())))
    except TypeError:
        return None


def build_dedup_cache_key(device_id: str, payload_hash: int) -> str:
    """Build cache key used by MQTT dedup map."""
    return f"{device_id}:{payload_hash}"


def is_duplicate_within_window(
    message_cache: Mapping[str, float],
    *,
    cache_key: str,
    current_time: float,
    dedup_window: float,
) -> bool:
    """Return True when message duplicates a recent payload for same device."""
    last_time = message_cache.get(cache_key)
    return last_time is not None and current_time - last_time < dedup_window


def cleanup_dedup_cache(
    message_cache: Mapping[str, float],
    *,
    current_time: float,
    stale_seconds: float,
    max_entries: int,
) -> dict[str, float]:
    """Return pruned dedup cache with stale entries removed and capped."""
    cleaned = {
        key: ts
        for key, ts in message_cache.items()
        if current_time - ts <= stale_seconds
    }

    if len(cleaned) <= max_entries:
        return cleaned

    sorted_items = sorted(cleaned.items(), key=lambda item: item[1])
    keep_from = len(sorted_items) // 2
    return dict(sorted_items[keep_from:])
