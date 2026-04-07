"""Binary-split execution helpers for REST status fallback queries."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import logging
from typing import Protocol

from .status_fallback_summary_logging import (
    log_batch_query_fallback,
    log_empty_fallback_summary,
)
from .types import JsonObject

type QueryPayload = JsonObject
type MappingRows = list[JsonObject]
type NormalizeResponseCode = Callable[[object], str | int | None]
type ExtractDataList = Callable[[object], MappingRows]
type IoTRequest = Callable[[str, QueryPayload], Awaitable[object]]
type IsRetriableDeviceError = Callable[[Exception], bool]


class _BinarySplitQueryContextLike(Protocol):
    path: str
    body_key: str
    item_name: str
    iot_request: IoTRequest
    extract_data_list: ExtractDataList
    is_retriable_device_error: IsRetriableDeviceError
    lipro_api_error: type[Exception]
    normalize_response_code: NormalizeResponseCode
    logger: logging.Logger

    async def query_rows(
        self,
        ids: list[str],
        *,
        semaphore: asyncio.Semaphore,
    ) -> MappingRows: ...

    def normalized_error_code(self, err: Exception) -> str: ...


class _BinarySplitAccumulatorLike(Protocol):
    rows: MappingRows
    failed_single_queries: int
    single_error_codes: dict[str, int]
    max_fallback_depth: int

    def extend_rows(self, rows: MappingRows) -> None: ...

    def record_depth(self, depth: int) -> None: ...

    def record_single_failure(
        self,
        *,
        context: _BinarySplitQueryContextLike,
        err: Exception,
        item_id: str,
    ) -> None: ...


class _BinarySplitQueryOptionsLike(Protocol):
    small_subset_batch_query_threshold: int
    small_subset_batch_size: int


type AccumulatorFactory = Callable[[], _BinarySplitAccumulatorLike]


async def _query_single_item(
    item_id: str,
    *,
    context: _BinarySplitQueryContextLike,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulatorLike,
) -> None:
    try:
        accumulator.extend_rows(
            await context.query_rows([item_id], semaphore=semaphore)
        )
    except context.lipro_api_error as err:
        if not context.is_retriable_device_error(err):
            raise
        accumulator.record_single_failure(
            context=context,
            err=err,
            item_id=item_id,
        )


async def query_items_individually_impl(
    item_ids: list[str],
    *,
    context: _BinarySplitQueryContextLike,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulatorLike,
) -> None:
    """Run per-item fallback queries in parallel under the provided semaphore."""
    await asyncio.gather(
        *(
            _query_single_item(
                item_id,
                context=context,
                semaphore=semaphore,
                accumulator=accumulator,
            )
            for item_id in item_ids
        )
    )


def split_subset_ids(subset: list[str]) -> tuple[list[str], list[str]]:
    """Split one subset into left/right halves for recursive fallback."""
    mid = len(subset) // 2
    return subset[:mid], subset[mid:]


async def _query_small_subset(
    subset: list[str],
    *,
    context: _BinarySplitQueryContextLike,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulatorLike,
    options: _BinarySplitQueryOptionsLike,
) -> None:
    if len(subset) <= options.small_subset_batch_size:
        await query_items_individually_impl(
            subset,
            context=context,
            semaphore=semaphore,
            accumulator=accumulator,
        )
        return

    for start in range(0, len(subset), options.small_subset_batch_size):
        batch = subset[start : start + options.small_subset_batch_size]
        try:
            accumulator.extend_rows(
                await context.query_rows(batch, semaphore=semaphore)
            )
        except context.lipro_api_error as err:
            if not context.is_retriable_device_error(err):
                raise
            await query_items_individually_impl(
                batch,
                context=context,
                semaphore=semaphore,
                accumulator=accumulator,
            )


async def _query_subset_batch(
    subset: list[str],
    *,
    context: _BinarySplitQueryContextLike,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulatorLike,
) -> bool:
    try:
        accumulator.extend_rows(await context.query_rows(subset, semaphore=semaphore))
        return True
    except context.lipro_api_error as err:
        if not context.is_retriable_device_error(err):
            raise
        return False


async def _query_subset(
    subset: list[str],
    *,
    depth: int,
    context: _BinarySplitQueryContextLike,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulatorLike,
    options: _BinarySplitQueryOptionsLike,
) -> None:
    if not subset:
        return

    accumulator.record_depth(depth)

    if len(subset) <= options.small_subset_batch_query_threshold:
        await _query_small_subset(
            subset,
            context=context,
            semaphore=semaphore,
            accumulator=accumulator,
            options=options,
        )
        return

    if await _query_subset_batch(
        subset,
        context=context,
        semaphore=semaphore,
        accumulator=accumulator,
    ):
        return

    left, right = split_subset_ids(subset)
    await asyncio.gather(
        _query_subset(
            left,
            depth=depth + 1,
            context=context,
            semaphore=semaphore,
            accumulator=accumulator,
            options=options,
        ),
        _query_subset(
            right,
            depth=depth + 1,
            context=context,
            semaphore=semaphore,
            accumulator=accumulator,
            options=options,
        ),
    )


async def query_binary_split_root_impl(
    ids: list[str],
    *,
    context: _BinarySplitQueryContextLike,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulatorLike,
    options: _BinarySplitQueryOptionsLike,
) -> None:
    """Start binary-split fallback from the full batch root."""
    if len(ids) <= options.small_subset_batch_query_threshold:
        await _query_subset(
            ids,
            depth=1,
            context=context,
            semaphore=semaphore,
            accumulator=accumulator,
            options=options,
        )
        return

    left, right = split_subset_ids(ids)
    await asyncio.gather(
        _query_subset(
            left,
            depth=2,
            context=context,
            semaphore=semaphore,
            accumulator=accumulator,
            options=options,
        ),
        _query_subset(
            right,
            depth=2,
            context=context,
            semaphore=semaphore,
            accumulator=accumulator,
            options=options,
        ),
    )


async def execute_binary_split_query(
    *,
    ids: list[str],
    context: _BinarySplitQueryContextLike,
    options: _BinarySplitQueryOptionsLike,
    accumulator_factory: AccumulatorFactory,
) -> tuple[MappingRows, int, dict[str, int], int]:
    """Execute the binary-split fallback tree and return accumulated results."""
    if not ids:
        return [], 0, {}, 0

    accumulator = accumulator_factory()
    await query_binary_split_root_impl(
        ids,
        context=context,
        semaphore=asyncio.Semaphore(min(5, len(ids))),
        accumulator=accumulator,
        options=options,
    )
    return (
        accumulator.rows,
        accumulator.failed_single_queries,
        accumulator.single_error_codes,
        accumulator.max_fallback_depth,
    )


async def execute_batch_fallback_query(
    *,
    context: _BinarySplitQueryContextLike,
    err: Exception,
    expected_offline_codes: tuple[int | str, ...],
    ids: list[str],
    options: _BinarySplitQueryOptionsLike,
    accumulator_factory: AccumulatorFactory,
) -> tuple[MappingRows, int]:
    """Log the triggering batch failure, then run binary-split fallback."""
    batch_code = log_batch_query_fallback(
        context=context,
        err=err,
        expected_offline_codes=expected_offline_codes,
    )
    (
        all_results,
        failed_single_queries,
        single_error_codes,
        max_fallback_depth,
    ) = await execute_binary_split_query(
        ids=ids,
        context=context,
        options=options,
        accumulator_factory=accumulator_factory,
    )
    log_empty_fallback_summary(
        path=context.path,
        item_name=context.item_name,
        batch_code=batch_code,
        ids=ids,
        all_results=all_results,
        failed_single_queries=failed_single_queries,
        single_error_codes=single_error_codes,
        logger=context.logger,
    )
    return all_results, max_fallback_depth


__all__ = [
    "execute_batch_fallback_query",
    "execute_binary_split_query",
    "query_binary_split_root_impl",
    "query_items_individually_impl",
    "split_subset_ids",
]
