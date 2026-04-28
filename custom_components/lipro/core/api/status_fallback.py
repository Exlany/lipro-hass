"""Binary-split fallback public home for REST status queries."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging
from typing import cast

from .status_fallback_support import (
    query_items_by_binary_split_impl,
    query_with_fallback_impl,
)
from .types import JsonObject, JsonValue

type QueryPayload = JsonObject
type MappingRows = list[JsonObject]
type NormalizeResponseCode = Callable[[object], str | int | None]
type ExtractDataList = Callable[[object], MappingRows]
type IoTRequest = Callable[[str, QueryPayload], Awaitable[object]]
type IsRetriableDeviceError = Callable[[Exception], bool]
type CoerceConnectStatus = Callable[[object], bool]
type SanitizeIoTDeviceIds = Callable[..., list[str]]
type RecordFallbackDepth = Callable[[int], None]
type RecordStatusBatchMetric = Callable[[int, float, int], None]

_SMALL_SUBSET_BATCH_QUERY_THRESHOLD = 4
_SMALL_SUBSET_BATCH_SIZE = 2
_STATE_QUERY_SOFT_MAX_BATCH_SIZE = 64


def _build_query_payload(body_key: str, ids: list[str]) -> QueryPayload:
    return {body_key: cast(JsonValue, ids)}


def _resolve_device_status_batch_size(
    *,
    total_devices: int,
    max_devices_per_query: int,
) -> int:
    """Resolve an effective batch size for state queries."""
    hard_cap = max(1, max_devices_per_query)
    if total_devices <= 0:
        return hard_cap
    if total_devices <= hard_cap <= _STATE_QUERY_SOFT_MAX_BATCH_SIZE:
        return total_devices
    return min(total_devices, hard_cap, _STATE_QUERY_SOFT_MAX_BATCH_SIZE)


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
    logger: logging.Logger,
) -> tuple[MappingRows, int, dict[str, int], int]:
    """Query items by recursively splitting failing batches."""
    return await query_items_by_binary_split_impl(
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
        build_query_payload=_build_query_payload,
        small_subset_batch_query_threshold=_SMALL_SUBSET_BATCH_QUERY_THRESHOLD,
        small_subset_batch_size=_SMALL_SUBSET_BATCH_SIZE,
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
    logger: logging.Logger,
    record_fallback_depth: RecordFallbackDepth | None = None,
) -> MappingRows:
    """Query API with binary-split fallback on retriable device errors."""
    return await query_with_fallback_impl(
        path=path,
        body_key=body_key,
        ids=ids,
        item_name=item_name,
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        is_retriable_device_error=is_retriable_device_error,
        lipro_api_error=lipro_api_error,
        normalize_response_code=normalize_response_code,
        expected_offline_codes=expected_offline_codes,
        logger=logger,
        build_query_payload=_build_query_payload,
        small_subset_batch_query_threshold=_SMALL_SUBSET_BATCH_QUERY_THRESHOLD,
        small_subset_batch_size=_SMALL_SUBSET_BATCH_SIZE,
        record_fallback_depth=record_fallback_depth,
    )


__all__ = [
    "CoerceConnectStatus",
    "ExtractDataList",
    "IoTRequest",
    "IsRetriableDeviceError",
    "MappingRows",
    "NormalizeResponseCode",
    "QueryPayload",
    "RecordStatusBatchMetric",
    "SanitizeIoTDeviceIds",
    "_query_items_by_binary_split",
    "_resolve_device_status_batch_size",
    "query_with_fallback",
]
