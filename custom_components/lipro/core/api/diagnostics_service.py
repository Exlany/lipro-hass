"""Diagnostic endpoint helpers for Lipro API client."""

from __future__ import annotations

import logging
from typing import Any, cast

from ...const.api import (
    PATH_FETCH_BODY_SENSOR_HISTORY,
    PATH_FETCH_DOOR_SENSOR_HISTORY,
    PATH_GET_CITY,
    PATH_QUERY_COMMAND_RESULT,
    PATH_QUERY_CONTROLLER_OTA,
    PATH_QUERY_OTA_INFO,
    PATH_QUERY_OTA_INFO_V2,
)
from ..utils.log_safety import safe_error_placeholder

_LOGGER = logging.getLogger(__name__)

type OtaRowDedupeKey = tuple[str, str, str, str, str]


def _ota_row_dedupe_key(row: dict[str, Any]) -> OtaRowDedupeKey:
    """Build stable dedupe key for one OTA row."""
    return (
        str(row.get("deviceId") or row.get("iotId") or "").strip().lower(),
        str(row.get("deviceType") or row.get("bleName") or row.get("productName") or "")
        .strip()
        .lower(),
        str(
            row.get("latestVersion")
            or row.get("firmwareVersion")
            or row.get("version")
            or ""
        )
        .strip()
        .lower(),
        str(row.get("firmwareUrl") or row.get("url") or "").strip().lower(),
        str(row.get("md5") or "").strip().lower(),
    )


def _merge_ota_rows(
    merged_rows: list[dict[str, Any]],
    seen_keys: set[OtaRowDedupeKey],
    rows: list[Any],
) -> None:
    """Merge OTA rows in order while dropping duplicates by semantic key."""
    for row in rows:
        if not isinstance(row, dict):
            continue
        key = _ota_row_dedupe_key(row)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        merged_rows.append(row)


async def query_command_result(
    *,
    request_iot_mapping: Any,
    require_mapping_response: Any,
    to_device_type_hex: Any,
    msg_sn: str,
    device_id: str,
    device_type: int | str,
) -> dict[str, Any]:
    """Query async command delivery result by message serial number."""
    result, _ = await request_iot_mapping(
        PATH_QUERY_COMMAND_RESULT,
        {
            "msgSn": msg_sn,
            "deviceId": device_id,
            "deviceType": to_device_type_hex(device_type),
        },
    )
    return cast(
        dict[str, Any],
        require_mapping_response(PATH_QUERY_COMMAND_RESULT, result),
    )


async def get_city(
    *,
    iot_request: Any,
    require_mapping_response: Any,
) -> dict[str, Any]:
    """Get current city metadata from IoT backend."""
    result = await iot_request(PATH_GET_CITY, {})
    return cast(dict[str, Any], require_mapping_response(PATH_GET_CITY, result))


async def query_ota_info(
    *,
    iot_request: Any,
    extract_data_list: Any,
    is_invalid_param_error_code: Any,
    to_device_type_hex: Any,
    lipro_api_error: type[Exception],
    device_id: str,
    device_type: int | str,
) -> list[dict[str, Any]]:
    """Query firmware OTA info for a device/group."""
    ota_payload = {
        "deviceId": device_id,
        "deviceType": to_device_type_hex(device_type),
    }

    merged_rows: list[dict[str, Any]] = []
    seen_keys: set[OtaRowDedupeKey] = set()

    ota_error: Exception | None = None
    ota_success = False
    for path in (PATH_QUERY_OTA_INFO, PATH_QUERY_OTA_INFO_V2):
        try:
            result = await iot_request(path, ota_payload)
        except lipro_api_error as err:
            ota_error = err
            _LOGGER.debug(
                "OTA endpoint %s failed (%s)",
                path,
                safe_error_placeholder(err),
            )
            continue

        _merge_ota_rows(
            merged_rows,
            seen_keys,
            extract_data_list(result),
        )
        ota_success = True

    if not ota_success and ota_error is not None:
        raise ota_error

    try:
        controller_result = await iot_request(PATH_QUERY_CONTROLLER_OTA, {})
    except lipro_api_error as err:
        code = getattr(err, "code", None)
        if is_invalid_param_error_code(code):
            _LOGGER.debug(
                "Controller OTA endpoint rejected payload (code=%s, err=%s)",
                code,
                safe_error_placeholder(err),
            )
        else:
            _LOGGER.debug(
                "Controller OTA endpoint %s failed (%s)",
                PATH_QUERY_CONTROLLER_OTA,
                safe_error_placeholder(err),
            )
    else:
        _merge_ota_rows(
            merged_rows,
            seen_keys,
            extract_data_list(controller_result),
        )

    return merged_rows


async def fetch_body_sensor_history(
    *,
    iot_request: Any,
    require_mapping_response: Any,
    to_device_type_hex: Any,
    device_id: str,
    device_type: int | str,
    sensor_device_id: str,
    mesh_type: str,
) -> dict[str, Any]:
    """Fetch body sensor history snapshot for diagnostics."""
    return await fetch_sensor_history(
        iot_request=iot_request,
        require_mapping_response=require_mapping_response,
        to_device_type_hex=to_device_type_hex,
        path=PATH_FETCH_BODY_SENSOR_HISTORY,
        device_id=device_id,
        device_type=device_type,
        sensor_device_id=sensor_device_id,
        mesh_type=mesh_type,
    )


async def fetch_door_sensor_history(
    *,
    iot_request: Any,
    require_mapping_response: Any,
    to_device_type_hex: Any,
    device_id: str,
    device_type: int | str,
    sensor_device_id: str,
    mesh_type: str,
) -> dict[str, Any]:
    """Fetch door sensor history snapshot for diagnostics."""
    return await fetch_sensor_history(
        iot_request=iot_request,
        require_mapping_response=require_mapping_response,
        to_device_type_hex=to_device_type_hex,
        path=PATH_FETCH_DOOR_SENSOR_HISTORY,
        device_id=device_id,
        device_type=device_type,
        sensor_device_id=sensor_device_id,
        mesh_type=mesh_type,
    )


async def fetch_sensor_history(
    *,
    iot_request: Any,
    require_mapping_response: Any,
    to_device_type_hex: Any,
    path: str,
    device_id: str,
    device_type: int | str,
    sensor_device_id: str,
    mesh_type: str,
) -> dict[str, Any]:
    """Fetch one sensor-history payload using shared request fields."""
    result = await iot_request(
        path,
        {
            "deviceId": device_id,
            "deviceType": to_device_type_hex(device_type),
            "sensorDeviceId": sensor_device_id,
            "meshType": mesh_type,
        },
    )
    return cast(dict[str, Any], require_mapping_response(path, result))
