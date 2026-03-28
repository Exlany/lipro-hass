"""Internal support implementation for REST status fallback queries."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
import logging

from .types import JsonObject

type QueryPayload = JsonObject
type MappingRows = list[JsonObject]
type NormalizeResponseCode = Callable[[object], str | int | None]
type ExtractDataList = Callable[[object], MappingRows]
type IoTRequest = Callable[[str, QueryPayload], Awaitable[object]]
type IsRetriableDeviceError = Callable[[Exception], bool]
type RecordFallbackDepth = Callable[[int], None]
type BuildQueryPayload = Callable[[str, list[str]], QueryPayload]


@dataclass(slots=True, frozen=True)
class _BinarySplitQueryContext:
    path: str
    body_key: str
    item_name: str
    iot_request: IoTRequest
    extract_data_list: ExtractDataList
    is_retriable_device_error: IsRetriableDeviceError
    lipro_api_error: type[Exception]
    normalize_response_code: NormalizeResponseCode
    logger: logging.Logger
    build_query_payload: BuildQueryPayload


@dataclass(slots=True)
class _BinarySplitAccumulator:
    rows: MappingRows = field(default_factory=list)
    failed_single_queries: int = 0
    single_error_codes: dict[str, int] = field(default_factory=dict)
    max_fallback_depth: int = 0

    def extend_rows(self, rows: MappingRows) -> None:
        if rows:
            self.rows.extend(rows)

    def record_depth(self, depth: int) -> None:
        self.max_fallback_depth = max(self.max_fallback_depth, depth)

    def record_single_failure(
        self,
        *,
        context: _BinarySplitQueryContext,
        err: Exception,
        item_id: str,
    ) -> None:
        normalized = context.normalize_response_code(getattr(err, 'code', None))
        single_code = str(normalized) if normalized is not None else 'unknown'
        context.logger.debug(
            'Failed to query %s %s: %s (code=%s, endpoint=%s)',
            context.item_name,
            item_id,
            err,
            single_code,
            context.path,
        )
        self.failed_single_queries += 1
        self.single_error_codes[single_code] = (
            self.single_error_codes.get(single_code, 0) + 1
        )


def log_batch_query_fallback(
    *,
    path: str,
    item_name: str,
    err: Exception,
    normalize_response_code: NormalizeResponseCode,
    expected_offline_codes: tuple[int | str, ...],
    logger: logging.Logger,
) -> str | int:
    normalized_code = normalize_response_code(getattr(err, 'code', None))
    if normalized_code is None:
        normalized_code = 'unknown'
    if normalized_code in expected_offline_codes:
        logger.debug(
            'Batch %s query failed with expected offline code (%s). Falling back to individual queries.',
            item_name,
            normalized_code,
        )
        return normalized_code

    logger.warning(
        'Batch %s query failed (code=%s, endpoint=%s): %s. Falling back to individual queries.',
        item_name,
        normalized_code,
        path,
        err,
    )
    return normalized_code


async def _query_single_item(
    item_id: str,
    *,
    context: _BinarySplitQueryContext,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulator,
) -> None:
    try:
        async with semaphore:
            result = await context.iot_request(
                context.path,
                context.build_query_payload(context.body_key, [item_id]),
            )
        accumulator.extend_rows(context.extract_data_list(result))
    except context.lipro_api_error as err:
        if not context.is_retriable_device_error(err):
            raise
        accumulator.record_single_failure(
            context=context,
            err=err,
            item_id=item_id,
        )


async def _query_small_subset(
    subset: list[str],
    *,
    context: _BinarySplitQueryContext,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulator,
    small_subset_batch_size: int,
) -> None:
    if len(subset) <= small_subset_batch_size:
        await asyncio.gather(
            *(
                _query_single_item(
                    item_id,
                    context=context,
                    semaphore=semaphore,
                    accumulator=accumulator,
                )
                for item_id in subset
            )
        )
        return

    for start in range(0, len(subset), small_subset_batch_size):
        batch = subset[start : start + small_subset_batch_size]
        try:
            async with semaphore:
                result = await context.iot_request(
                    context.path,
                    context.build_query_payload(context.body_key, batch),
                )
            accumulator.extend_rows(context.extract_data_list(result))
        except context.lipro_api_error as err:
            if not context.is_retriable_device_error(err):
                raise
            await asyncio.gather(
                *(
                    _query_single_item(
                        item_id,
                        context=context,
                        semaphore=semaphore,
                        accumulator=accumulator,
                    )
                    for item_id in batch
                )
            )


async def _query_subset(
    subset: list[str],
    *,
    depth: int,
    context: _BinarySplitQueryContext,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulator,
    small_subset_batch_query_threshold: int,
    small_subset_batch_size: int,
) -> None:
    if not subset:
        return

    accumulator.record_depth(depth)

    if len(subset) <= small_subset_batch_query_threshold:
        await _query_small_subset(
            subset,
            context=context,
            semaphore=semaphore,
            accumulator=accumulator,
            small_subset_batch_size=small_subset_batch_size,
        )
        return

    try:
        async with semaphore:
            result = await context.iot_request(
                context.path,
                context.build_query_payload(context.body_key, subset),
            )
        accumulator.extend_rows(context.extract_data_list(result))
        return
    except context.lipro_api_error as err:
        if not context.is_retriable_device_error(err):
            raise

    mid = len(subset) // 2
    await asyncio.gather(
        _query_subset(
            subset[:mid],
            depth=depth + 1,
            context=context,
            semaphore=semaphore,
            accumulator=accumulator,
            small_subset_batch_query_threshold=small_subset_batch_query_threshold,
            small_subset_batch_size=small_subset_batch_size,
        ),
        _query_subset(
            subset[mid:],
            depth=depth + 1,
            context=context,
            semaphore=semaphore,
            accumulator=accumulator,
            small_subset_batch_query_threshold=small_subset_batch_query_threshold,
            small_subset_batch_size=small_subset_batch_size,
        ),
    )


async def query_items_by_binary_split_impl(
    *,
    path: str,
    body_key: str,
    ids: list[str],
    item_name: str,
    iot_request: IoTRequest,
    extract_data_list: ExtractDataList,
    is_retriable_device_error: IsRetriableDeviceError,
    lipro_api_error: type[Exception],
    normalize_response_code: NormalizeResponseCode,
    logger: logging.Logger,
    build_query_payload: BuildQueryPayload,
    small_subset_batch_query_threshold: int,
    small_subset_batch_size: int,
) -> tuple[MappingRows, int, dict[str, int], int]:
    """Query items by recursively splitting failing batches."""
    if not ids:
        return [], 0, {}, 0

    context = _BinarySplitQueryContext(
        path=path,
        body_key=body_key,
        item_name=item_name,
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        is_retriable_device_error=is_retriable_device_error,
        lipro_api_error=lipro_api_error,
        normalize_response_code=normalize_response_code,
        logger=logger,
        build_query_payload=build_query_payload,
    )
    accumulator = _BinarySplitAccumulator()
    semaphore = asyncio.Semaphore(min(5, len(ids)))

    if len(ids) <= small_subset_batch_query_threshold:
        await _query_subset(
            ids,
            depth=1,
            context=context,
            semaphore=semaphore,
            accumulator=accumulator,
            small_subset_batch_query_threshold=small_subset_batch_query_threshold,
            small_subset_batch_size=small_subset_batch_size,
        )
    else:
        mid = len(ids) // 2
        await asyncio.gather(
            _query_subset(
                ids[:mid],
                depth=2,
                context=context,
                semaphore=semaphore,
                accumulator=accumulator,
                small_subset_batch_query_threshold=small_subset_batch_query_threshold,
                small_subset_batch_size=small_subset_batch_size,
            ),
            _query_subset(
                ids[mid:],
                depth=2,
                context=context,
                semaphore=semaphore,
                accumulator=accumulator,
                small_subset_batch_query_threshold=small_subset_batch_query_threshold,
                small_subset_batch_size=small_subset_batch_size,
            ),
        )

    return (
        accumulator.rows,
        accumulator.failed_single_queries,
        accumulator.single_error_codes,
        accumulator.max_fallback_depth,
    )


def log_empty_fallback_summary(
    *,
    path: str,
    item_name: str,
    batch_code: str | int,
    ids: list[str],
    all_results: MappingRows,
    failed_single_queries: int,
    single_error_codes: dict[str, int],
    logger: logging.Logger,
) -> None:
    if not ids or all_results or failed_single_queries != len(ids):
        return

    dominant_single_code = (
        max(single_error_codes.items(), key=lambda item: item[1])[0]
        if single_error_codes
        else 'unknown'
    )
    logger.warning(
        'Batch %s query fallback returned no data: %d/%d single queries failed (batch_code=%s, dominant_single_code=%s, endpoint=%s)',
        item_name,
        failed_single_queries,
        len(ids),
        batch_code,
        dominant_single_code,
        path,
    )


async def query_with_fallback_impl(
    *,
    path: str,
    body_key: str,
    ids: list[str],
    item_name: str,
    iot_request: IoTRequest,
    extract_data_list: ExtractDataList,
    is_retriable_device_error: IsRetriableDeviceError,
    lipro_api_error: type[Exception],
    normalize_response_code: NormalizeResponseCode,
    expected_offline_codes: tuple[int | str, ...],
    logger: logging.Logger,
    build_query_payload: BuildQueryPayload,
    small_subset_batch_query_threshold: int,
    small_subset_batch_size: int,
    record_fallback_depth: RecordFallbackDepth | None = None,
) -> MappingRows:
    """Query API with binary-split fallback on retriable device errors."""
    try:
        result = await iot_request(path, build_query_payload(body_key, ids))
        if record_fallback_depth is not None:
            record_fallback_depth(0)
        return extract_data_list(result)
    except lipro_api_error as err:
        if not is_retriable_device_error(err):
            raise

        batch_code = log_batch_query_fallback(
            path=path,
            item_name=item_name,
            err=err,
            normalize_response_code=normalize_response_code,
            expected_offline_codes=expected_offline_codes,
            logger=logger,
        )
        (
            all_results,
            failed_single_queries,
            single_error_codes,
            max_fallback_depth,
        ) = await query_items_by_binary_split_impl(
            path=path,
            body_key=body_key,
            ids=ids,
            item_name=item_name,
            iot_request=iot_request,
            extract_data_list=extract_data_list,
            is_retriable_device_error=is_retriable_device_error,
            lipro_api_error=lipro_api_error,
            normalize_response_code=normalize_response_code,
            logger=logger,
            build_query_payload=build_query_payload,
            small_subset_batch_query_threshold=small_subset_batch_query_threshold,
            small_subset_batch_size=small_subset_batch_size,
        )
        if record_fallback_depth is not None:
            record_fallback_depth(max_fallback_depth)
        log_empty_fallback_summary(
            path=path,
            item_name=item_name,
            batch_code=batch_code,
            ids=ids,
            all_results=all_results,
            failed_single_queries=failed_single_queries,
            single_error_codes=single_error_codes,
            logger=logger,
        )
        return all_results


__all__ = [
    'query_items_by_binary_split_impl',
    'query_with_fallback_impl',
]
