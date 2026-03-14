"""Shared OTA rows caching primitives."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from .row_selector import OtaDeviceFingerprint, arbitrate_rows

OTA_SHARED_ROWS_CACHE_TTL = timedelta(minutes=10)
OTA_SHARED_ROWS_CACHE_MAX_ENTRIES = 256

type OtaRowsCacheKey = tuple[object, str, str, int]


@dataclass(slots=True)
class OtaRowsCacheEntry:
    """Shared OTA rows cache entry for model-scoped lookups."""

    time: datetime
    rows: list[dict[str, Any]]


_OTA_ROWS_CACHE: dict[OtaRowsCacheKey, OtaRowsCacheEntry] = {}
_OTA_ROWS_INFLIGHT: dict[OtaRowsCacheKey, asyncio.Task[list[dict[str, Any]]]] = {}
_OTA_ROWS_CACHE_LOCK = asyncio.Lock()


def _coerce_cache_product_id(product_id: int | str | None) -> int:
    try:
        return int(product_id or 0)
    except (TypeError, ValueError):
        return 0


def build_ota_rows_cache_key(
    coordinator: object,
    *,
    device_type: str,
    iot_name: str | None,
    product_id: int | str | None,
) -> OtaRowsCacheKey:
    """Build the shared OTA cache key for one model-like OTA identity."""
    return (
        coordinator,
        str(device_type).strip().lower(),
        str(iot_name or "").strip().lower(),
        _coerce_cache_product_id(product_id),
    )


def normalize_ota_rows(rows: object) -> list[dict[str, object]]:
    """Normalize OTA cloud payloads into a stable list-of-dicts shape."""
    if not isinstance(rows, list):
        return []
    return [dict(row) for row in rows if isinstance(row, dict)]


def clear_shared_ota_rows_cache() -> None:
    """Clear shared OTA rows cache (intended for tests)."""
    _OTA_ROWS_CACHE.clear()
    _OTA_ROWS_INFLIGHT.clear()


def is_cache_entry_fresh(entry: OtaRowsCacheEntry, now: datetime) -> bool:
    """Return whether a shared OTA cache entry is still valid."""
    return now - entry.time < OTA_SHARED_ROWS_CACHE_TTL


def prune_ota_rows_cache(now: datetime) -> None:
    """Prune OTA shared cache by TTL and hard size cap."""
    stale_keys = [
        key
        for key, entry in _OTA_ROWS_CACHE.items()
        if now - entry.time >= OTA_SHARED_ROWS_CACHE_TTL
    ]
    for stale_key in stale_keys:
        _OTA_ROWS_CACHE.pop(stale_key, None)

    overflow = len(_OTA_ROWS_CACHE) - OTA_SHARED_ROWS_CACHE_MAX_ENTRIES
    if overflow <= 0:
        return

    oldest_items = sorted(
        _OTA_ROWS_CACHE.items(),
        key=lambda item: item[1].time,
    )[:overflow]
    for cache_key, _ in oldest_items:
        _OTA_ROWS_CACHE.pop(cache_key, None)


async def async_get_rows_with_shared_cache(
    cache_key: OtaRowsCacheKey,
    *,
    fetcher: Callable[[], Coroutine[Any, Any, list[dict[str, Any]]]],
    now: Callable[[], datetime],
) -> tuple[list[dict[str, Any]], bool]:
    """Query OTA rows with model-scoped shared cache and in-flight dedup."""
    now_time = now()
    cached = _OTA_ROWS_CACHE.get(cache_key)
    if cached and is_cache_entry_fresh(cached, now_time):
        return cached.rows, True

    creator = False
    task: asyncio.Task[list[dict[str, Any]]]
    async with _OTA_ROWS_CACHE_LOCK:
        now_time = now()
        cached = _OTA_ROWS_CACHE.get(cache_key)
        if cached and is_cache_entry_fresh(cached, now_time):
            return cached.rows, True

        inflight = _OTA_ROWS_INFLIGHT.get(cache_key)
        if inflight is None:
            inflight = asyncio.create_task(fetcher())
            _OTA_ROWS_INFLIGHT[cache_key] = inflight
            creator = True
        task = inflight

    try:
        rows = await task
    finally:
        if creator:
            async with _OTA_ROWS_CACHE_LOCK:
                _OTA_ROWS_INFLIGHT.pop(cache_key, None)

    now_time = now()
    async with _OTA_ROWS_CACHE_LOCK:
        _OTA_ROWS_CACHE[cache_key] = OtaRowsCacheEntry(
            time=now_time,
            rows=rows,
        )
        prune_ota_rows_cache(now_time)
    return rows, False


async def async_select_row_with_shared_cache(
    cache_key: OtaRowsCacheKey,
    *,
    fetcher: Callable[[], Coroutine[Any, Any, list[dict[str, Any]]]],
    now: Callable[[], datetime],
    fingerprint: OtaDeviceFingerprint,
) -> dict[str, Any] | None:
    """Select one OTA row, bypassing cache when it points at another device."""
    rows, from_cache = await async_get_rows_with_shared_cache(
        cache_key,
        fetcher=fetcher,
        now=now,
    )
    arbitration = arbitrate_rows(
        rows,
        fingerprint=fingerprint,
        from_cache=from_cache,
    )
    if not arbitration.should_retry_without_cache:
        return arbitration.selected_row

    fresh_rows = await fetcher()
    return arbitrate_rows(
        fresh_rows,
        fingerprint=fingerprint,
        from_cache=False,
    ).selected_row
