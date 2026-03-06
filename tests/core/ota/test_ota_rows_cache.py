"""Tests for shared OTA rows cache helpers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from custom_components.lipro.core.ota import rows_cache


def test_prune_ota_rows_cache_removes_stale_entries() -> None:
    now = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)

    rows_cache.clear_shared_ota_rows_cache()
    try:
        owner = object()
        stale_key = (owner, "model_a", "type_a", 1)
        fresh_key = (owner, "model_a", "type_a", 2)

        rows_cache._OTA_ROWS_CACHE[stale_key] = rows_cache.OtaRowsCacheEntry(
            time=now - rows_cache.OTA_SHARED_ROWS_CACHE_TTL - timedelta(seconds=1),
            rows=[],
        )
        rows_cache._OTA_ROWS_CACHE[fresh_key] = rows_cache.OtaRowsCacheEntry(
            time=now,
            rows=[],
        )

        rows_cache.prune_ota_rows_cache(now)

        assert stale_key not in rows_cache._OTA_ROWS_CACHE
        assert fresh_key in rows_cache._OTA_ROWS_CACHE
    finally:
        rows_cache.clear_shared_ota_rows_cache()
