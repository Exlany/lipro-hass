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
class _RetriableBatchQueryError(Exception):
    error: Exception


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

    def build_payload(self, ids: list[str]) -> QueryPayload:
        return self.build_query_payload(self.body_key, ids)

    async def query_rows(
        self,
        ids: list[str],
        *,
        semaphore: asyncio.Semaphore,
    ) -> MappingRows:
        async with semaphore:
            result = await self.iot_request(
                self.path,
                self.build_payload(ids),
            )
        return self.extract_data_list(result)

    def normalized_error_code(self, err: Exception) -> str:
        normalized = self.normalize_response_code(getattr(err, "code", None))
        return str(normalized) if normalized is not None else "unknown"


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
        single_code = context.normalized_error_code(err)
        context.logger.debug(
            "Failed to query %s %s: %s (code=%s, endpoint=%s)",
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


@dataclass(slots=True, frozen=True)
class _BinarySplitQueryOptions:
    small_subset_batch_query_threshold: int
    small_subset_batch_size: int


@dataclass(slots=True, frozen=True)
class _BinarySplitSetup:
    context: _BinarySplitQueryContext
    options: _BinarySplitQueryOptions


def _build_query_options(
    *,
    small_subset_batch_query_threshold: int,
    small_subset_batch_size: int,
) -> _BinarySplitQueryOptions:
    if small_subset_batch_query_threshold < 0:
        raise ValueError(
            "small_subset_batch_query_threshold must be greater than or equal to 0"
        )
    if small_subset_batch_size <= 0:
        raise ValueError("small_subset_batch_size must be greater than 0")
    return _BinarySplitQueryOptions(
        small_subset_batch_query_threshold=small_subset_batch_query_threshold,
        small_subset_batch_size=small_subset_batch_size,
    )


def _build_query_context(
    *,
    path: str,
    body_key: str,
    item_name: str,
    iot_request: IoTRequest,
    extract_data_list: ExtractDataList,
    is_retriable_device_error: IsRetriableDeviceError,
    lipro_api_error: type[Exception],
    normalize_response_code: NormalizeResponseCode,
    logger: logging.Logger,
    build_query_payload: BuildQueryPayload,
) -> _BinarySplitQueryContext:
    return _BinarySplitQueryContext(
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


def _record_fallback_depth_if_needed(
    record_fallback_depth: RecordFallbackDepth | None,
    depth: int,
) -> None:
    if record_fallback_depth is not None:
        record_fallback_depth(depth)


def _build_binary_split_setup(
    *,
    path: str,
    body_key: str,
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
) -> _BinarySplitSetup:
    return _BinarySplitSetup(
        context=_build_query_context(
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
        ),
        options=_build_query_options(
            small_subset_batch_query_threshold=small_subset_batch_query_threshold,
            small_subset_batch_size=small_subset_batch_size,
        ),
    )


def _build_binary_split_result(
    accumulator: _BinarySplitAccumulator,
) -> tuple[MappingRows, int, dict[str, int], int]:
    return (
        accumulator.rows,
        accumulator.failed_single_queries,
        accumulator.single_error_codes,
        accumulator.max_fallback_depth,
    )


def log_batch_query_fallback(
    *,
    context: _BinarySplitQueryContext,
    err: Exception,
    expected_offline_codes: tuple[int | str, ...],
) -> str | int:
    normalized_code = context.normalize_response_code(getattr(err, "code", None))
    if normalized_code is None:
        normalized_code = "unknown"
    if normalized_code in expected_offline_codes:
        context.logger.debug(
            "Batch %s query failed with expected offline code (%s). Falling back to individual queries.",
            context.item_name,
            normalized_code,
        )
        return normalized_code

    context.logger.warning(
        "Batch %s query failed (code=%s, endpoint=%s): %s. Falling back to individual queries.",
        context.item_name,
        normalized_code,
        context.path,
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


async def _query_items_individually(
    item_ids: list[str],
    *,
    context: _BinarySplitQueryContext,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulator,
) -> None:
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


async def _query_small_subset(
    subset: list[str],
    *,
    context: _BinarySplitQueryContext,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulator,
    options: _BinarySplitQueryOptions,
) -> None:
    if len(subset) <= options.small_subset_batch_size:
        await _query_items_individually(
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
            await _query_items_individually(
                batch,
                context=context,
                semaphore=semaphore,
                accumulator=accumulator,
            )


def _split_subset_ids(subset: list[str]) -> tuple[list[str], list[str]]:
    mid = len(subset) // 2
    return subset[:mid], subset[mid:]


async def _query_subset(
    subset: list[str],
    *,
    depth: int,
    context: _BinarySplitQueryContext,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulator,
    options: _BinarySplitQueryOptions,
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

    await _query_subset_branches(
        subset,
        depth=depth,
        context=context,
        semaphore=semaphore,
        accumulator=accumulator,
        options=options,
    )


async def _query_binary_split_root(
    ids: list[str],
    *,
    context: _BinarySplitQueryContext,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulator,
    options: _BinarySplitQueryOptions,
) -> None:
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

    left, right = _split_subset_ids(ids)
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
    setup = _build_binary_split_setup(
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
        small_subset_batch_query_threshold=small_subset_batch_query_threshold,
        small_subset_batch_size=small_subset_batch_size,
    )
    accumulator = _BinarySplitAccumulator()
    await _query_binary_split_root(
        ids,
        context=setup.context,
        semaphore=asyncio.Semaphore(min(5, len(ids))),
        accumulator=accumulator,
        options=setup.options,
    )
    return _build_binary_split_result(accumulator)


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
        else "unknown"
    )
    logger.warning(
        "Batch %s query fallback returned no data: %d/%d single queries failed (batch_code=%s, dominant_single_code=%s, endpoint=%s)",
        item_name,
        failed_single_queries,
        len(ids),
        batch_code,
        dominant_single_code,
        path,
    )


async def _query_with_batch_fallback(
    *,
    context: _BinarySplitQueryContext,
    err: Exception,
    expected_offline_codes: tuple[int | str, ...],
    ids: list[str],
    options: _BinarySplitQueryOptions,
) -> tuple[MappingRows, int]:
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
    ) = await query_items_by_binary_split_impl(
        path=context.path,
        body_key=context.body_key,
        ids=ids,
        item_name=context.item_name,
        iot_request=context.iot_request,
        extract_data_list=context.extract_data_list,
        is_retriable_device_error=context.is_retriable_device_error,
        lipro_api_error=context.lipro_api_error,
        normalize_response_code=context.normalize_response_code,
        logger=context.logger,
        build_query_payload=context.build_query_payload,
        small_subset_batch_query_threshold=options.small_subset_batch_query_threshold,
        small_subset_batch_size=options.small_subset_batch_size,
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


async def _query_subset_batch(
    subset: list[str],
    *,
    context: _BinarySplitQueryContext,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulator,
) -> bool:
    try:
        accumulator.extend_rows(await context.query_rows(subset, semaphore=semaphore))
        return True
    except context.lipro_api_error as err:
        if not context.is_retriable_device_error(err):
            raise
        return False


async def _query_subset_branches(
    subset: list[str],
    *,
    depth: int,
    context: _BinarySplitQueryContext,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulator,
    options: _BinarySplitQueryOptions,
) -> None:
    left, right = _split_subset_ids(subset)
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


async def _query_primary_batch(
    *,
    context: _BinarySplitQueryContext,
    ids: list[str],
) -> MappingRows:
    try:
        return await context.query_rows(ids, semaphore=asyncio.Semaphore(1))
    except context.lipro_api_error as err:
        if not context.is_retriable_device_error(err):
            raise
        raise _RetriableBatchQueryError(error=err) from err


async def _query_with_retriable_fallback(
    *,
    context: _BinarySplitQueryContext,
    err: Exception,
    expected_offline_codes: tuple[int | str, ...],
    ids: list[str],
    options: _BinarySplitQueryOptions,
    record_fallback_depth: RecordFallbackDepth | None,
) -> MappingRows:
    all_results, max_fallback_depth = await _query_with_batch_fallback(
        context=context,
        err=err,
        expected_offline_codes=expected_offline_codes,
        ids=ids,
        options=options,
    )
    _record_fallback_depth_if_needed(
        record_fallback_depth,
        max_fallback_depth,
    )
    return all_results


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
    setup = _build_binary_split_setup(
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
        small_subset_batch_query_threshold=small_subset_batch_query_threshold,
        small_subset_batch_size=small_subset_batch_size,
    )
    try:
        result_rows = await _query_primary_batch(
            context=setup.context,
            ids=ids,
        )
        _record_fallback_depth_if_needed(record_fallback_depth, 0)
        return result_rows
    except _RetriableBatchQueryError as failure:
        return await _query_with_retriable_fallback(
            context=setup.context,
            err=failure.error,
            expected_offline_codes=expected_offline_codes,
            ids=ids,
            options=setup.options,
            record_fallback_depth=record_fallback_depth,
        )


__all__ = [
    "query_items_by_binary_split_impl",
    "query_with_fallback_impl",
]
