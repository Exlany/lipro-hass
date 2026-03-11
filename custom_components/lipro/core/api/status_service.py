"""Status endpoint helpers for Lipro API client."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from time import monotonic
from typing import Any

from .types import DeviceStatusItem

type MappingPayload = dict[str, Any]
type MappingRows = list[MappingPayload]
type NormalizeResponseCode = Callable[[Any], str | int | None]
type ExtractDataList = Callable[[Any], MappingRows]
type IoTRequest = Callable[[str, MappingPayload], Awaitable[Any]]
type IsRetriableDeviceError = Callable[[Exception], bool]
type CoerceConnectStatus = Callable[[Any], bool]
type SanitizeIoTDeviceIds = Callable[..., list[str]]
type RecordFallbackDepth = Callable[[int], None]
type RecordStatusBatchMetric = Callable[[int, float, int], None]

_SMALL_SUBSET_BATCH_QUERY_THRESHOLD = 4
_SMALL_SUBSET_BATCH_SIZE = 2
# Keep state batches below cloud timeout-sensitive sizes observed in field tests.
_STATE_QUERY_SOFT_MAX_BATCH_SIZE = 64


def _resolve_device_status_batch_size(
    *,
    total_devices: int,
    max_devices_per_query: int,
) -> int:
    """Resolve an effective batch size for state queries.

    Strategy:
    - Respect caller-provided hard cap.
    - Keep large-fleet state batches under a softer ceiling to avoid long-tail
      latency and timeout amplification when payload grows linearly.
    """
    hard_cap = max(1, max_devices_per_query)
    if total_devices <= 0:
        return hard_cap
    if total_devices <= hard_cap <= _STATE_QUERY_SOFT_MAX_BATCH_SIZE:
        return total_devices
    return min(total_devices, hard_cap, _STATE_QUERY_SOFT_MAX_BATCH_SIZE)


def _log_batch_query_fallback(
    *,
    path: str,
    item_name: str,
    err: Exception,
    normalize_response_code: NormalizeResponseCode,
    expected_offline_codes: tuple[int | str, ...],
    logger: Any,
) -> str | int:
    normalized_code = normalize_response_code(getattr(err, "code", None))
    if normalized_code is None:
        normalized_code = "unknown"
    if normalized_code in expected_offline_codes:
        logger.debug(
            "Batch %s query failed with expected offline code (%s). "
            "Falling back to individual queries.",
            item_name,
            normalized_code,
        )
        return normalized_code

    logger.warning(
        "Batch %s query failed (code=%s, endpoint=%s): %s. "
        "Falling back to individual queries.",
        item_name,
        normalized_code,
        path,
        err,
    )
    return normalized_code


async def _query_items_by_binary_split(
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
    logger: Any,
) -> tuple[MappingRows, int, dict[str, int], int]:
    """Query items by recursively splitting failing batches.

    This is a divide-and-conquer fallback that isolates problematic IDs while
    keeping batching benefits for healthy subsets.
    """
    all_results: MappingRows = []
    failed_single_queries = 0
    single_error_codes: dict[str, int] = {}
    max_fallback_depth = 0

    if not ids:
        return (
            all_results,
            failed_single_queries,
            single_error_codes,
            max_fallback_depth,
        )

    # Bound total in-flight API calls to avoid event-loop spikes.
    max_concurrency = min(5, len(ids))
    semaphore = asyncio.Semaphore(max_concurrency)

    def _record_single_failure(err: Exception, item_id: str) -> None:
        nonlocal failed_single_queries
        normalized = normalize_response_code(getattr(err, "code", None))
        single_code = str(normalized) if normalized is not None else "unknown"
        logger.debug(
            "Failed to query %s %s: %s (code=%s, endpoint=%s)",
            item_name,
            item_id,
            err,
            single_code,
            path,
        )
        failed_single_queries += 1
        single_error_codes[single_code] = single_error_codes.get(single_code, 0) + 1

    async def _query_single(item_id: str) -> None:
        try:
            async with semaphore:
                result = await iot_request(path, {body_key: [item_id]})
            rows = extract_data_list(result)
            if rows:
                all_results.extend(rows)
        except lipro_api_error as err:
            if not is_retriable_device_error(err):
                raise
            _record_single_failure(err, item_id)

    async def _query_small_subset(subset: list[str]) -> None:
        if len(subset) <= 2:
            await asyncio.gather(*(_query_single(item_id) for item_id in subset))
            return

        for start in range(0, len(subset), _SMALL_SUBSET_BATCH_SIZE):
            batch = subset[start : start + _SMALL_SUBSET_BATCH_SIZE]
            try:
                async with semaphore:
                    result = await iot_request(path, {body_key: batch})
                rows = extract_data_list(result)
                if rows:
                    all_results.extend(rows)
            except lipro_api_error as err:
                if not is_retriable_device_error(err):
                    raise
                await asyncio.gather(*(_query_single(item_id) for item_id in batch))

    async def _query_subset(subset: list[str], depth: int) -> None:
        nonlocal max_fallback_depth
        if not subset:
            return
        max_fallback_depth = max(max_fallback_depth, depth)
        if len(subset) <= _SMALL_SUBSET_BATCH_QUERY_THRESHOLD:
            await _query_small_subset(subset)
            return

        try:
            async with semaphore:
                result = await iot_request(path, {body_key: subset})
            rows = extract_data_list(result)
            if rows:
                all_results.extend(rows)
            return
        except lipro_api_error as err:
            if not is_retriable_device_error(err):
                raise

            mid = len(subset) // 2
            await asyncio.gather(
                _query_subset(subset[:mid], depth + 1),
                _query_subset(subset[mid:], depth + 1),
            )

    # The top-level batch call already failed in query_with_fallback.
    # Start from sub-batches to avoid re-requesting the same full ID list.
    if len(ids) <= _SMALL_SUBSET_BATCH_QUERY_THRESHOLD:
        await _query_subset(ids, 1)
    else:
        mid = len(ids) // 2
        # Preserve fallback-depth semantics: this branch represents the first
        # split level after the already-failed top-level batch request.
        await asyncio.gather(
            _query_subset(ids[:mid], 2),
            _query_subset(ids[mid:], 2),
        )

    return all_results, failed_single_queries, single_error_codes, max_fallback_depth


def _log_empty_fallback_summary(
    *,
    path: str,
    item_name: str,
    batch_code: str | int,
    ids: list[str],
    all_results: list[dict[str, Any]],
    failed_single_queries: int,
    single_error_codes: dict[str, int],
    logger: Any,
) -> None:
    if not ids or all_results or failed_single_queries != len(ids):
        return

    dominant_single_code = (
        max(single_error_codes.items(), key=lambda item: item[1])[0]
        if single_error_codes
        else "unknown"
    )
    logger.warning(
        "Batch %s query fallback returned no data: %d/%d single queries failed "
        "(batch_code=%s, dominant_single_code=%s, endpoint=%s)",
        item_name,
        failed_single_queries,
        len(ids),
        batch_code,
        dominant_single_code,
        path,
    )


async def query_with_fallback(
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
    logger: Any,
    record_fallback_depth: RecordFallbackDepth | None = None,
) -> MappingRows:
    """Query API with binary-split fallback on retriable device errors."""
    try:
        result = await iot_request(path, {body_key: ids})
        if record_fallback_depth is not None:
            record_fallback_depth(0)
        return extract_data_list(result)
    except lipro_api_error as err:
        if not is_retriable_device_error(err):
            raise

        batch_code = _log_batch_query_fallback(
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
        ) = await _query_items_by_binary_split(
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
        )
        if record_fallback_depth is not None:
            record_fallback_depth(max_fallback_depth)
        _log_empty_fallback_summary(
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


async def query_device_status(
    *,
    device_ids: list[str],
    max_devices_per_query: int,
    iot_request: IoTRequest,
    extract_data_list: ExtractDataList,
    is_retriable_device_error: IsRetriableDeviceError,
    lipro_api_error: type[Exception],
    normalize_response_code: NormalizeResponseCode,
    expected_offline_codes: tuple[int | str, ...],
    logger: Any,
    path_query_device_status: str,
    on_batch_metric: RecordStatusBatchMetric | None = None,
) -> list[DeviceStatusItem]:
    """Query status of multiple devices using batching and binary-split fallback."""
    if not device_ids:
        return []

    effective_batch_size = _resolve_device_status_batch_size(
        total_devices=len(device_ids),
        max_devices_per_query=max_devices_per_query,
    )
    if (
        effective_batch_size != max_devices_per_query
        and len(device_ids) > effective_batch_size
    ):
        logger.debug(
            "Adaptive state batch size applied: total=%d configured=%d effective=%d",
            len(device_ids),
            max_devices_per_query,
            effective_batch_size,
        )

    batches = [
        device_ids[i : i + effective_batch_size]
        for i in range(0, len(device_ids), effective_batch_size)
    ]

    # Keep batch concurrency small to avoid rate limits with many devices.
    max_concurrency = min(3, len(batches))
    semaphore = asyncio.Semaphore(max_concurrency)

    async def _query_batch(batch: list[str]) -> MappingRows:
        fallback_depth = 0

        def _record_fallback_depth(depth: int) -> None:
            nonlocal fallback_depth
            fallback_depth = max(fallback_depth, depth)

        started_at = monotonic()
        async with semaphore:
            rows = await query_with_fallback(
                path=path_query_device_status,
                body_key="deviceIdList",
                ids=batch,
                item_name="device",
                iot_request=iot_request,
                extract_data_list=extract_data_list,
                is_retriable_device_error=is_retriable_device_error,
                lipro_api_error=lipro_api_error,
                normalize_response_code=normalize_response_code,
                expected_offline_codes=expected_offline_codes,
                logger=logger,
                record_fallback_depth=_record_fallback_depth,
            )
        if on_batch_metric is not None:
            on_batch_metric(
                len(batch),
                max(0.0, monotonic() - started_at),
                fallback_depth,
            )
        return rows

    if len(batches) == 1:
        return await _query_batch(batches[0])

    results = await asyncio.gather(*(_query_batch(batch) for batch in batches))
    all_results: MappingRows = []
    for rows in results:
        if rows:
            all_results.extend(rows)
    return all_results


async def query_mesh_group_status(
    *,
    group_ids: list[str],
    iot_request: IoTRequest,
    extract_data_list: ExtractDataList,
    is_retriable_device_error: IsRetriableDeviceError,
    lipro_api_error: type[Exception],
    normalize_response_code: NormalizeResponseCode,
    expected_offline_codes: tuple[int | str, ...],
    logger: Any,
    path_query_mesh_group_status: str,
) -> MappingRows:
    """Query status of mesh groups with per-group fallback behavior."""
    if not group_ids:
        return []

    return await query_with_fallback(
        path=path_query_mesh_group_status,
        body_key="groupIdList",
        ids=group_ids,
        item_name="group",
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        is_retriable_device_error=is_retriable_device_error,
        lipro_api_error=lipro_api_error,
        normalize_response_code=normalize_response_code,
        expected_offline_codes=expected_offline_codes,
        logger=logger,
    )


async def query_connect_status(
    *,
    device_ids: list[str],
    sanitize_iot_device_ids: SanitizeIoTDeviceIds,
    iot_request: IoTRequest,
    coerce_connect_status: CoerceConnectStatus,
    lipro_api_error: type[Exception],
    logger: Any,
    path_query_connect_status: str,
) -> dict[str, bool]:
    """Query real-time connection status for devices."""
    if not device_ids:
        return {}

    sanitized_ids = sanitize_iot_device_ids(
        device_ids,
        endpoint=path_query_connect_status,
    )
    if not sanitized_ids:
        return {}

    try:
        # _iot_request returns Any; keep defensive decoding for payload variants.
        result: Any = await iot_request(
            path_query_connect_status,
            {"deviceIdList": sanitized_ids},
        )
        if isinstance(result, dict):
            if "code" in result and "data" in result:
                wrapped_data = result.get("data")
                if isinstance(wrapped_data, dict):
                    result = wrapped_data
                else:
                    return {}
            return {k: coerce_connect_status(v) for k, v in result.items()}
        return {}
    except lipro_api_error as err:
        logger.debug(
            "Failed to query connect status (device_count=%d): %s",
            len(device_ids),
            err,
        )
        return {}
