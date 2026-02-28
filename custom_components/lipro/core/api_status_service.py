"""Status endpoint helpers for Lipro API client."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

type MappingPayload = dict[str, Any]
type MappingRows = list[MappingPayload]
type NormalizeResponseCode = Callable[[Any], str | int | None]
type ExtractDataList = Callable[[Any], MappingRows]
type IoTRequest = Callable[[str, MappingPayload], Awaitable[Any]]
type IsRetriableDeviceError = Callable[[Exception], bool]
type CoerceConnectStatus = Callable[[Any], bool]
type SanitizeIoTDeviceIds = Callable[..., list[str]]


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


async def _query_items_individually(
    *,
    path: str,
    body_key: str,
    ids: list[str],
    item_name: str,
    iot_request: IoTRequest,
    extract_data_list: ExtractDataList,
    lipro_api_error: type[Exception],
    normalize_response_code: NormalizeResponseCode,
    logger: Any,
) -> tuple[MappingRows, int, dict[str, int]]:
    all_results: MappingRows = []
    failed_single_queries = 0
    single_error_codes: dict[str, int] = {}

    for item_id in ids:
        try:
            single_result = await iot_request(path, {body_key: [item_id]})
            all_results.extend(extract_data_list(single_result))
        except lipro_api_error as single_err:
            failed_single_queries += 1
            single_code = str(
                normalize_response_code(getattr(single_err, "code", None)),
            )
            single_error_codes[single_code] = single_error_codes.get(single_code, 0) + 1
            logger.debug(
                "Failed to query %s %s: %s (code=%s, endpoint=%s)",
                item_name,
                item_id,
                single_err,
                single_code,
                path,
            )

    return all_results, failed_single_queries, single_error_codes


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
) -> MappingRows:
    """Query API with fallback to individual queries on retriable device errors."""
    try:
        result = await iot_request(path, {body_key: ids})
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
        ) = await _query_items_individually(
            path=path,
            body_key=body_key,
            ids=ids,
            item_name=item_name,
            iot_request=iot_request,
            extract_data_list=extract_data_list,
            lipro_api_error=lipro_api_error,
            normalize_response_code=normalize_response_code,
            logger=logger,
        )
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
) -> MappingRows:
    """Query status of multiple devices with batch fallback behavior."""
    if not device_ids:
        return []

    all_results: MappingRows = []
    for i in range(0, len(device_ids), max_devices_per_query):
        batch = device_ids[i : i + max_devices_per_query]
        all_results.extend(
            await query_with_fallback(
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
            )
        )
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
            "Failed to query connect status for %s: %s",
            device_ids,
            err,
        )
        return {}
