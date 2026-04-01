"""Internal support implementation for REST status fallback queries."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
import logging

from .status_fallback_split_executor import (
    execute_batch_fallback_query,
    execute_binary_split_query,
    query_binary_split_root_impl,
    query_items_individually_impl,
    split_subset_ids,
)
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


async def _query_items_individually(
    item_ids: list[str],
    *,
    context: _BinarySplitQueryContext,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulator,
) -> None:
    await query_items_individually_impl(
        item_ids,
        context=context,
        semaphore=semaphore,
        accumulator=accumulator,
    )


def _split_subset_ids(subset: list[str]) -> tuple[list[str], list[str]]:
    return split_subset_ids(subset)


async def _query_binary_split_root(
    ids: list[str],
    *,
    context: _BinarySplitQueryContext,
    semaphore: asyncio.Semaphore,
    accumulator: _BinarySplitAccumulator,
    options: _BinarySplitQueryOptions,
) -> None:
    await query_binary_split_root_impl(
        ids,
        context=context,
        semaphore=semaphore,
        accumulator=accumulator,
        options=options,
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
    return await execute_binary_split_query(
        ids=ids,
        context=setup.context,
        options=setup.options,
        accumulator_factory=_BinarySplitAccumulator,
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
    if not ids:
        _record_fallback_depth_if_needed(record_fallback_depth, 0)
        return []

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
        result_rows = await setup.context.query_rows(ids, semaphore=asyncio.Semaphore(1))
    except setup.context.lipro_api_error as err:
        if not setup.context.is_retriable_device_error(err):
            raise
        all_results, max_fallback_depth = await execute_batch_fallback_query(
            context=setup.context,
            err=err,
            expected_offline_codes=expected_offline_codes,
            ids=ids,
            options=setup.options,
            accumulator_factory=_BinarySplitAccumulator,
        )
        _record_fallback_depth_if_needed(record_fallback_depth, max_fallback_depth)
        return all_results

    _record_fallback_depth_if_needed(record_fallback_depth, 0)
    return result_rows


__all__ = [
    "query_items_by_binary_split_impl",
    "query_with_fallback_impl",
]
