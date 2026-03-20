"""Diagnostic endpoint helpers for Lipro API client."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass
import logging
from typing import cast

from custom_components.lipro.core.api.types import JsonObject, JsonValue, OtaInfoRow

from ...const.api import (
    PATH_FETCH_BODY_SENSOR_HISTORY,
    PATH_FETCH_DOOR_SENSOR_HISTORY,
    PATH_GET_CITY,
    PATH_QUERY_COMMAND_RESULT,
    PATH_QUERY_CONTROLLER_OTA,
    PATH_QUERY_OTA_INFO,
    PATH_QUERY_OTA_INFO_V2,
    PATH_QUERY_USER_CLOUD,
)
from ..telemetry.models import (
    OperationOutcome,
    build_operation_outcome,
    build_operation_outcome_from_exception,
)
from ..utils.log_safety import safe_error_placeholder

_LOGGER = logging.getLogger(__name__)

type ResponseMapping = JsonObject
type RequestPayload = JsonObject
type OtaRowDedupeKey = tuple[str, str, str, str, str]
type RequestIotMapping = Callable[..., Awaitable[tuple[JsonObject, str | None]]]
type RequestIotMappingRaw = Callable[..., Awaitable[tuple[JsonObject, str | None]]]
type IotRequest = Callable[..., Awaitable[JsonValue]]
type RequireMappingResponse = Callable[[str, object], JsonObject]
type ExtractDataList = Callable[[object], Sequence[object]]
type DeviceTypeHexResolver = Callable[[int | str], str]
type InvalidParamCodeChecker = Callable[[object], bool]

_OTA_FAILURE_ORIGIN = "diagnostics.query_ota_info"


@dataclass(frozen=True, slots=True)
class OtaQueryResult:
    """Rows plus one typed outcome for OTA diagnostics probing."""

    rows: list[OtaInfoRow]
    outcome: OperationOutcome
    error: Exception | None = None


def _valid_ota_rows(rows: Sequence[object]) -> list[OtaInfoRow]:
    """Keep OTA rows that are valid mapping objects."""
    return [cast(OtaInfoRow, row) for row in rows if isinstance(row, dict)]


def _build_rich_ota_v2_payload(
    ota_payload: Mapping[str, object],
    *,
    iot_name: str | None,
    allow_rich_v2_fallback: bool,
) -> dict[str, object] | None:
    """Build richer OTA v2 payload for devices that benefit from hasMacRule."""
    if not allow_rich_v2_fallback:
        return None
    normalized_iot_name = str(iot_name or "").strip()
    if not normalized_iot_name:
        return None
    return {
        **dict(ota_payload),
        "iotName": normalized_iot_name,
        "skuId": "",
        "hasMacRule": True,
    }


def _ota_row_dedupe_key(row: Mapping[str, object]) -> OtaRowDedupeKey:
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
    merged_rows: list[OtaInfoRow],
    seen_keys: set[OtaRowDedupeKey],
    rows: Sequence[object],
) -> None:
    """Merge OTA rows in order while dropping duplicates by semantic key."""
    for row in rows:
        if not isinstance(row, dict):
            continue
        key = _ota_row_dedupe_key(row)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        merged_rows.append(cast(OtaInfoRow, row))


def _extract_http_status_from_error(err: Exception) -> int | None:
    code = getattr(err, "code", None)
    return code if isinstance(code, int) else None


def _api_error_outcome(err: Exception, *, kind: str, reason_code: str) -> OperationOutcome:
    return build_operation_outcome_from_exception(
        err,
        kind=cast(object, kind),
        reason_code=reason_code,
        failure_origin=_OTA_FAILURE_ORIGIN,
        failure_category="protocol",
        handling_policy="inspect",
        http_status=_extract_http_status_from_error(err),
    )


def _resolve_ota_query_outcome(
    *,
    primary_failure_recovered: bool,
    rich_v2_recovered: bool,
    rich_v2_outcome: OperationOutcome | None,
    controller_outcome: OperationOutcome | None,
) -> OperationOutcome:
    if primary_failure_recovered:
        return build_operation_outcome(
            kind="degraded",
            reason_code="primary_endpoint_recovered",
        )
    if rich_v2_recovered:
        return build_operation_outcome(
            kind="degraded",
            reason_code="rich_v2_recovered",
        )
    if rich_v2_outcome is not None:
        return rich_v2_outcome
    if controller_outcome is not None:
        return controller_outcome
    return build_operation_outcome(kind="success", reason_code="ota_query_complete")


async def query_command_result(
    *,
    request_iot_mapping: RequestIotMapping,
    require_mapping_response: RequireMappingResponse,
    to_device_type_hex: DeviceTypeHexResolver,
    msg_sn: str,
    device_id: str,
    device_type: int | str,
) -> ResponseMapping:
    """Query async command delivery result by message serial number."""
    result, _ = await request_iot_mapping(
        PATH_QUERY_COMMAND_RESULT,
        {
            "msgSn": msg_sn,
            "deviceId": device_id,
            "deviceType": to_device_type_hex(device_type),
        },
    )
    return require_mapping_response(PATH_QUERY_COMMAND_RESULT, result)


async def get_city(
    *,
    iot_request: IotRequest,
    require_mapping_response: RequireMappingResponse,
) -> ResponseMapping:
    """Get current city metadata from IoT backend."""
    result = await iot_request(PATH_GET_CITY, {})
    return require_mapping_response(PATH_GET_CITY, result)


async def query_user_cloud(
    *,
    request_iot_mapping_raw: RequestIotMappingRaw,
    require_mapping_response: RequireMappingResponse,
) -> ResponseMapping:
    """Query cloud-assistant metadata using the verified empty-string contract."""
    result, _ = await request_iot_mapping_raw(PATH_QUERY_USER_CLOUD, "")
    return require_mapping_response(PATH_QUERY_USER_CLOUD, result)


async def query_ota_info_with_outcome(
    *,
    iot_request: IotRequest,
    extract_data_list: ExtractDataList,
    is_invalid_param_error_code: InvalidParamCodeChecker,
    to_device_type_hex: DeviceTypeHexResolver,
    lipro_api_error: type[Exception],
    device_id: str,
    device_type: int | str,
    iot_name: str | None = None,
    allow_rich_v2_fallback: bool = False,
) -> OtaQueryResult:
    """Query firmware OTA info while exposing one typed outcome envelope."""
    ota_payload: RequestPayload = {
        "deviceId": device_id,
        "deviceType": to_device_type_hex(device_type),
    }
    rich_v2_payload = _build_rich_ota_v2_payload(
        ota_payload,
        iot_name=iot_name,
        allow_rich_v2_fallback=allow_rich_v2_fallback,
    )

    merged_rows: list[OtaInfoRow] = []
    seen_keys: set[OtaRowDedupeKey] = set()
    v1_rows: list[OtaInfoRow] = []
    v2_rows: list[OtaInfoRow] = []

    ota_error: Exception | None = None
    ota_success = False
    v1_failed = False
    v2_failed = False
    rich_v2_recovered = False
    rich_v2_outcome: OperationOutcome | None = None
    controller_outcome: OperationOutcome | None = None

    try:
        result = await iot_request(PATH_QUERY_OTA_INFO, ota_payload)
    except lipro_api_error as err:
        ota_error = err
        v1_failed = True
        _LOGGER.debug(
            "OTA endpoint %s failed (%s)",
            PATH_QUERY_OTA_INFO,
            safe_error_placeholder(err),
        )
    else:
        v1_rows = _valid_ota_rows(extract_data_list(result))
        _merge_ota_rows(merged_rows, seen_keys, v1_rows)
        ota_success = True

    try:
        result = await iot_request(PATH_QUERY_OTA_INFO_V2, ota_payload)
    except lipro_api_error as err:
        ota_error = err
        v2_failed = True
        _LOGGER.debug(
            "OTA endpoint %s failed (%s)",
            PATH_QUERY_OTA_INFO_V2,
            safe_error_placeholder(err),
        )
    else:
        ota_success = True
        v2_rows = _valid_ota_rows(extract_data_list(result))
        _merge_ota_rows(merged_rows, seen_keys, v2_rows)
        if not v1_rows and not v2_rows and rich_v2_payload is not None:
            try:
                rich_v2_result = await iot_request(PATH_QUERY_OTA_INFO_V2, rich_v2_payload)
            except lipro_api_error as err:
                ota_error = err
                code = getattr(err, "code", None)
                if is_invalid_param_error_code(code):
                    _LOGGER.debug(
                        "OTA endpoint %s rejected richer payload (code=%s, err=%s)",
                        PATH_QUERY_OTA_INFO_V2,
                        code,
                        safe_error_placeholder(err),
                    )
                    rich_v2_outcome = _api_error_outcome(
                        err,
                        kind="degraded",
                        reason_code="rich_v2_invalid_param",
                    )
                else:
                    _LOGGER.debug(
                        "OTA endpoint %s richer payload failed (%s)",
                        PATH_QUERY_OTA_INFO_V2,
                        safe_error_placeholder(err),
                    )
                    rich_v2_outcome = _api_error_outcome(
                        err,
                        kind="degraded",
                        reason_code="rich_v2_failed",
                    )
            else:
                ota_success = True
                rich_v2_rows = _valid_ota_rows(extract_data_list(rich_v2_result))
                _merge_ota_rows(merged_rows, seen_keys, rich_v2_rows)
                rich_v2_recovered = bool(rich_v2_rows)

    if not ota_success and ota_error is not None:
        return OtaQueryResult(
            rows=[],
            outcome=_api_error_outcome(
                ota_error,
                kind="failed",
                reason_code="primary_endpoints_failed",
            ),
            error=ota_error,
        )

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
            controller_outcome = _api_error_outcome(
                err,
                kind="degraded",
                reason_code="controller_invalid_param",
            )
        else:
            _LOGGER.debug(
                "Controller OTA endpoint %s failed (%s)",
                PATH_QUERY_CONTROLLER_OTA,
                safe_error_placeholder(err),
            )
            controller_outcome = _api_error_outcome(
                err,
                kind="degraded",
                reason_code="controller_failed",
            )
    else:
        _merge_ota_rows(merged_rows, seen_keys, extract_data_list(controller_result))

    outcome = _resolve_ota_query_outcome(
        primary_failure_recovered=(v1_failed or v2_failed) and ota_success,
        rich_v2_recovered=rich_v2_recovered,
        rich_v2_outcome=rich_v2_outcome,
        controller_outcome=controller_outcome,
    )
    return OtaQueryResult(rows=merged_rows, outcome=outcome)


async def query_ota_info(
    *,
    iot_request: IotRequest,
    extract_data_list: ExtractDataList,
    is_invalid_param_error_code: InvalidParamCodeChecker,
    to_device_type_hex: DeviceTypeHexResolver,
    lipro_api_error: type[Exception],
    device_id: str,
    device_type: int | str,
    iot_name: str | None = None,
    allow_rich_v2_fallback: bool = False,
) -> list[OtaInfoRow]:
    """Query firmware OTA info for a device/group."""
    result = await query_ota_info_with_outcome(
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        is_invalid_param_error_code=is_invalid_param_error_code,
        to_device_type_hex=to_device_type_hex,
        lipro_api_error=lipro_api_error,
        device_id=device_id,
        device_type=device_type,
        iot_name=iot_name,
        allow_rich_v2_fallback=allow_rich_v2_fallback,
    )
    if result.error is not None:
        raise result.error
    return result.rows


async def fetch_body_sensor_history(
    *,
    iot_request: IotRequest,
    require_mapping_response: RequireMappingResponse,
    to_device_type_hex: DeviceTypeHexResolver,
    device_id: str,
    device_type: int | str,
    sensor_device_id: str,
    mesh_type: str,
) -> ResponseMapping:
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
    iot_request: IotRequest,
    require_mapping_response: RequireMappingResponse,
    to_device_type_hex: DeviceTypeHexResolver,
    device_id: str,
    device_type: int | str,
    sensor_device_id: str,
    mesh_type: str,
) -> ResponseMapping:
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
    iot_request: IotRequest,
    require_mapping_response: RequireMappingResponse,
    to_device_type_hex: DeviceTypeHexResolver,
    path: str,
    device_id: str,
    device_type: int | str,
    sensor_device_id: str,
    mesh_type: str,
) -> ResponseMapping:
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
    return require_mapping_response(path, result)
