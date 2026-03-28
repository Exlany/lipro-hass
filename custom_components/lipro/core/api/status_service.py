"""Status endpoint helpers for Lipro API client."""

from __future__ import annotations

import asyncio
import logging
from time import monotonic
from typing import cast

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
    semaphore = asyncio.Semaphore(min(3, len(batches)))

    if len(batches) == 1:
        return await _query_status_batch(
            batches[0],
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

    results = await asyncio.gather(
        *(
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
        )
    )

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
    if not device_ids:
        return {}

    sanitized_ids = sanitize_iot_device_ids(
        device_ids,
        endpoint=path_query_connect_status,
    )
    if not sanitized_ids:
        return {}

    try:
        result = await iot_request(
            path_query_connect_status,
            {"deviceIdList": cast(JsonValue, sanitized_ids)},
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
