"""Status endpoint helpers for Lipro API client."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Mapping
from dataclasses import dataclass
from enum import StrEnum
import logging
from time import monotonic
from typing import cast

from ..utils.log_safety import safe_error_placeholder
from .status_fallback import (
    CoerceConnectStatus,
    ExtractDataList,
    IoTRequest,
    IsRetriableDeviceError,
    MappingRows,
    NormalizeResponseCode,
    RecordStatusBatchMetric,
    SanitizeIoTDeviceIds,
    _resolve_device_status_batch_size,
    query_with_fallback,
)
from .types import DeviceStatusItem, JsonValue


def _build_device_status_batches(
    *,
    device_ids: list[str],
    batch_size: int,
) -> list[list[str]]:
    return [
        device_ids[i : i + batch_size] for i in range(0, len(device_ids), batch_size)
    ]


def _log_adaptive_batch_size(
    *,
    device_count: int,
    configured_batch_size: int,
    effective_batch_size: int,
    logger: logging.Logger,
) -> None:
    if (
        effective_batch_size != configured_batch_size
        and device_count > effective_batch_size
    ):
        logger.debug(
            "Adaptive state batch size applied: total=%d configured=%d effective=%d",
            device_count,
            configured_batch_size,
            effective_batch_size,
        )


async def _query_status_batch(
    batch: list[str],
    *,
    semaphore: asyncio.Semaphore,
    path_query_device_status: str,
    iot_request: IoTRequest,
    extract_data_list: ExtractDataList,
    is_retriable_device_error: IsRetriableDeviceError,
    lipro_api_error: type[Exception],
    normalize_response_code: NormalizeResponseCode,
    expected_offline_codes: tuple[int | str, ...],
    logger: logging.Logger,
    on_batch_metric: RecordStatusBatchMetric | None,
) -> MappingRows:
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


def _build_status_batch_tasks(
    batches: list[list[str]],
    *,
    semaphore: asyncio.Semaphore,
    path_query_device_status: str,
    iot_request: IoTRequest,
    extract_data_list: ExtractDataList,
    is_retriable_device_error: IsRetriableDeviceError,
    lipro_api_error: type[Exception],
    normalize_response_code: NormalizeResponseCode,
    expected_offline_codes: tuple[int | str, ...],
    logger: logging.Logger,
    on_batch_metric: RecordStatusBatchMetric | None,
) -> list[Awaitable[MappingRows]]:
    """Build the batch-query awaitables for one device-status request."""
    return [
        _query_status_batch(
            batch,
            semaphore=semaphore,
            path_query_device_status=path_query_device_status,
            iot_request=iot_request,
            extract_data_list=extract_data_list,
            is_retriable_device_error=is_retriable_device_error,
            lipro_api_error=lipro_api_error,
            normalize_response_code=normalize_response_code,
            expected_offline_codes=expected_offline_codes,
            logger=logger,
            on_batch_metric=on_batch_metric,
        )
        for batch in batches
    ]


def _merge_status_batch_rows(results: list[MappingRows]) -> list[DeviceStatusItem]:
    """Flatten batch rows while preserving the typed outward result contract."""
    merged: MappingRows = []
    for rows in results:
        if rows:
            merged.extend(rows)
    return merged


async def _query_status_batches(
    batches: list[list[str]],
    *,
    semaphore: asyncio.Semaphore,
    path_query_device_status: str,
    iot_request: IoTRequest,
    extract_data_list: ExtractDataList,
    is_retriable_device_error: IsRetriableDeviceError,
    lipro_api_error: type[Exception],
    normalize_response_code: NormalizeResponseCode,
    expected_offline_codes: tuple[int | str, ...],
    logger: logging.Logger,
    on_batch_metric: RecordStatusBatchMetric | None,
) -> list[MappingRows]:
    """Execute one or more device-status batches with shared concurrency limits."""
    tasks = _build_status_batch_tasks(
        batches,
        semaphore=semaphore,
        path_query_device_status=path_query_device_status,
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        is_retriable_device_error=is_retriable_device_error,
        lipro_api_error=lipro_api_error,
        normalize_response_code=normalize_response_code,
        expected_offline_codes=expected_offline_codes,
        logger=logger,
        on_batch_metric=on_batch_metric,
    )
    if len(tasks) == 1:
        return [await tasks[0]]
    return list(await asyncio.gather(*tasks))


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
    logger: logging.Logger,
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
    _log_adaptive_batch_size(
        device_count=len(device_ids),
        configured_batch_size=max_devices_per_query,
        effective_batch_size=effective_batch_size,
        logger=logger,
    )

    batches = _build_device_status_batches(
        device_ids=device_ids,
        batch_size=effective_batch_size,
    )
    results = await _query_status_batches(
        batches,
        semaphore=asyncio.Semaphore(min(3, len(batches))),
        path_query_device_status=path_query_device_status,
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        is_retriable_device_error=is_retriable_device_error,
        lipro_api_error=lipro_api_error,
        normalize_response_code=normalize_response_code,
        expected_offline_codes=expected_offline_codes,
        logger=logger,
        on_batch_metric=on_batch_metric,
    )
    return _merge_status_batch_rows(results)


async def query_mesh_group_status(
    *,
    group_ids: list[str],
    iot_request: IoTRequest,
    extract_data_list: ExtractDataList,
    is_retriable_device_error: IsRetriableDeviceError,
    lipro_api_error: type[Exception],
    normalize_response_code: NormalizeResponseCode,
    expected_offline_codes: tuple[int | str, ...],
    logger: logging.Logger,
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


class ConnectStatusOutcome(StrEnum):
    """Internal outcome markers for connect-status query parsing."""

    SUCCESS = "success"
    EMPTY_INPUT = "empty_input"
    EMPTY_SANITIZED = "empty_sanitized"
    NON_MAPPING = "non_mapping"
    WRAPPED_NON_MAPPING = "wrapped_non_mapping"
    EMPTY_MAPPING = "empty_mapping"
    API_ERROR = "api_error"


@dataclass(frozen=True, slots=True)
class _ConnectStatusQueryResult:
    """Typed internal result that preserves failure reasons for observability."""

    outcome: ConnectStatusOutcome
    statuses: dict[str, bool]


def _unwrap_connect_status_mapping(
    payload: object,
) -> tuple[ConnectStatusOutcome, Mapping[object, object] | None]:
    """Return the raw connect-status mapping together with its parse outcome."""
    if not isinstance(payload, Mapping):
        return ConnectStatusOutcome.NON_MAPPING, None

    mapping: Mapping[object, object] = payload
    if "code" in mapping and "data" in mapping:
        wrapped_data = mapping.get("data")
        if not isinstance(wrapped_data, Mapping):
            return ConnectStatusOutcome.WRAPPED_NON_MAPPING, None
        mapping = wrapped_data

    if not mapping:
        return ConnectStatusOutcome.EMPTY_MAPPING, mapping
    return ConnectStatusOutcome.SUCCESS, mapping


def _project_connect_status_mapping(
    mapping: Mapping[object, object],
    *,
    requested_ids: list[str],
    coerce_connect_status: CoerceConnectStatus,
) -> dict[str, bool]:
    """Project raw backend data onto the sanitized request set only."""
    return {
        device_id: coerce_connect_status(mapping[device_id])
        for device_id in requested_ids
        if device_id in mapping
    }


async def _query_connect_status_result(
    *,
    device_ids: list[str],
    sanitize_iot_device_ids: SanitizeIoTDeviceIds,
    iot_request: IoTRequest,
    coerce_connect_status: CoerceConnectStatus,
    lipro_api_error: type[Exception],
    logger: logging.Logger,
    path_query_connect_status: str,
) -> _ConnectStatusQueryResult:
    """Return the projected connect-status mapping plus an explicit parse outcome."""
    if not device_ids:
        return _ConnectStatusQueryResult(ConnectStatusOutcome.EMPTY_INPUT, {})

    sanitized_ids = sanitize_iot_device_ids(
        device_ids,
        endpoint=path_query_connect_status,
    )
    if not sanitized_ids:
        return _ConnectStatusQueryResult(ConnectStatusOutcome.EMPTY_SANITIZED, {})

    try:
        payload = await iot_request(
            path_query_connect_status,
            {"deviceIdList": cast(JsonValue, sanitized_ids)},
        )
    except lipro_api_error as err:
        logger.debug(
            "Failed to query connect status (device_count=%d): %s",
            len(sanitized_ids),
            safe_error_placeholder(err),
        )
        return _ConnectStatusQueryResult(ConnectStatusOutcome.API_ERROR, {})

    outcome, mapping = _unwrap_connect_status_mapping(payload)
    if mapping is None:
        logger.debug(
            "Connect status query returned %s payload (device_count=%d)",
            outcome.value,
            len(sanitized_ids),
        )
        return _ConnectStatusQueryResult(outcome, {})

    statuses = _project_connect_status_mapping(
        mapping,
        requested_ids=sanitized_ids,
        coerce_connect_status=coerce_connect_status,
    )
    return _ConnectStatusQueryResult(outcome, statuses)


async def query_connect_status(
    *,
    device_ids: list[str],
    sanitize_iot_device_ids: SanitizeIoTDeviceIds,
    iot_request: IoTRequest,
    coerce_connect_status: CoerceConnectStatus,
    lipro_api_error: type[Exception],
    logger: logging.Logger,
    path_query_connect_status: str,
) -> dict[str, bool]:
    """Query real-time connection status for devices."""
    result = await _query_connect_status_result(
        device_ids=device_ids,
        sanitize_iot_device_ids=sanitize_iot_device_ids,
        iot_request=iot_request,
        coerce_connect_status=coerce_connect_status,
        lipro_api_error=lipro_api_error,
        logger=logger,
        path_query_connect_status=path_query_connect_status,
    )
    return result.statuses
