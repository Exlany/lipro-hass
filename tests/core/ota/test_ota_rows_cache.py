"""Tests for shared OTA rows cache helpers."""

from __future__ import annotations

import asyncio
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.core.ota import rows_cache


@pytest.fixture(autouse=True)
def _clear_shared_cache() -> Iterator[None]:
    rows_cache.clear_shared_ota_rows_cache()
    yield
    rows_cache.clear_shared_ota_rows_cache()


def test_prune_ota_rows_cache_removes_stale_entries() -> None:
    now = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)

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


@pytest.mark.asyncio
async def test_async_get_rows_with_shared_cache_hits_fresh_cache() -> None:
    now = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    cache_key = (object(), "model_a", "type_a", 1)
    cached_rows: rows_cache.OtaRows = [{"latestVersion": "1.0.1"}]
    rows_cache._OTA_ROWS_CACHE[cache_key] = rows_cache.OtaRowsCacheEntry(
        time=now,
        rows=cached_rows,
    )
    fetcher = AsyncMock(return_value=[{"latestVersion": "9.9.9"}])

    rows, from_cache = await rows_cache.async_get_rows_with_shared_cache(
        cache_key,
        fetcher=fetcher,
        now=lambda: now,
    )

    assert rows == cached_rows
    assert from_cache is True
    fetcher.assert_not_awaited()


@pytest.mark.asyncio
async def test_async_get_rows_with_shared_cache_deduplicates_inflight_fetches() -> None:
    now = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    cache_key = (object(), "model_a", "type_a", 1)
    release_fetch = asyncio.Event()
    rows: rows_cache.OtaRows = [{"latestVersion": "1.0.2"}]
    fetch_calls = 0

    async def fetcher() -> rows_cache.OtaRows:
        nonlocal fetch_calls
        fetch_calls += 1
        await release_fetch.wait()
        return rows

    first = asyncio.create_task(
        rows_cache.async_get_rows_with_shared_cache(
            cache_key,
            fetcher=fetcher,
            now=lambda: now,
        )
    )
    second = asyncio.create_task(
        rows_cache.async_get_rows_with_shared_cache(
            cache_key,
            fetcher=fetcher,
            now=lambda: now,
        )
    )
    await asyncio.sleep(0)
    release_fetch.set()

    first_result, second_result = await asyncio.gather(first, second)

    assert fetch_calls == 1
    assert first_result == (rows, False)
    assert second_result == (rows, False)
    assert rows_cache._OTA_ROWS_CACHE[cache_key].rows == rows
    assert cache_key not in rows_cache._OTA_ROWS_INFLIGHT


@pytest.mark.asyncio
async def test_async_get_rows_with_shared_cache_clears_failed_inflight_state() -> None:
    now = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    cache_key = (object(), "model_a", "type_a", 1)
    failing_fetcher = AsyncMock(side_effect=RuntimeError("boom"))

    with pytest.raises(RuntimeError, match="boom"):
        await rows_cache.async_get_rows_with_shared_cache(
            cache_key,
            fetcher=failing_fetcher,
            now=lambda: now,
        )

    assert cache_key not in rows_cache._OTA_ROWS_INFLIGHT
    assert cache_key not in rows_cache._OTA_ROWS_CACHE

    recovery_rows: rows_cache.OtaRows = [{"latestVersion": "1.0.3"}]
    recovery_fetcher = AsyncMock(return_value=recovery_rows)
    rows, from_cache = await rows_cache.async_get_rows_with_shared_cache(
        cache_key,
        fetcher=recovery_fetcher,
        now=lambda: now,
    )

    assert rows == recovery_rows
    assert from_cache is False
    recovery_fetcher.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_get_rows_with_shared_cache_refreshes_stale_entry() -> None:
    now = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    cache_key = (object(), "model_a", "type_a", 1)
    stale_rows: rows_cache.OtaRows = [{"latestVersion": "1.0.0"}]
    fresh_rows: rows_cache.OtaRows = [{"latestVersion": "1.0.4"}]
    rows_cache._OTA_ROWS_CACHE[cache_key] = rows_cache.OtaRowsCacheEntry(
        time=now - rows_cache.OTA_SHARED_ROWS_CACHE_TTL - timedelta(seconds=1),
        rows=stale_rows,
    )
    fetcher = AsyncMock(return_value=fresh_rows)

    rows, from_cache = await rows_cache.async_get_rows_with_shared_cache(
        cache_key,
        fetcher=fetcher,
        now=lambda: now,
    )

    assert rows == fresh_rows
    assert from_cache is False
    fetcher.assert_awaited_once()
    assert rows_cache._OTA_ROWS_CACHE[cache_key].rows == fresh_rows
