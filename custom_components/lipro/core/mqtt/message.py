"""MQTT message normalization and deduplication helpers."""

from __future__ import annotations

from collections.abc import Hashable, Mapping
import heapq
from operator import itemgetter
from typing import Any, TypeVar

from ..utils.coerce import coerce_boollike

type DedupCacheKey = tuple[str, int]
K = TypeVar("K", bound=Hashable)


def is_online_connect_state(value: Any) -> bool:
    """Normalize connect-state payload variants to an online/offline boolean."""
    return coerce_boollike(value)


def compute_properties_hash(properties: dict[str, Any]) -> int | None:
    """Build stable hash for MQTT property payload deduplication.

    Returns ``None`` when payload values are not hashable.
    """
    try:
        # Avoid O(n log n) sorting; order-independent hashing is sufficient.
        return hash(frozenset(properties.items()))
    except TypeError:
        return None


def build_dedup_cache_key(device_id: str, payload_hash: int) -> DedupCacheKey:
    """Build cache key used by MQTT dedup map."""
    return (device_id, payload_hash)


def is_duplicate_within_window(
    message_cache: Mapping[K, float],
    *,
    cache_key: K,
    current_time: float,
    dedup_window: float,
) -> bool:
    """Return True when message duplicates a recent payload for same device."""
    last_time = message_cache.get(cache_key)
    return last_time is not None and current_time - last_time < dedup_window


def cleanup_dedup_cache(
    message_cache: Mapping[K, float],
    *,
    current_time: float,
    stale_seconds: float,
    max_entries: int,
) -> dict[K, float]:
    """Return pruned dedup cache with stale entries removed and capped."""
    if not message_cache:
        return {}

    cutoff = current_time - stale_seconds
    cleaned = {key: ts for key, ts in message_cache.items() if ts >= cutoff}

    cleaned_size = len(cleaned)
    if cleaned_size <= max_entries:
        return cleaned

    keep_from = cleaned_size // 2
    keep_count = cleaned_size - keep_from
    newest_items = heapq.nlargest(keep_count, cleaned.items(), key=itemgetter(1))
    return dict(newest_items)
