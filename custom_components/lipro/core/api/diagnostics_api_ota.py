"""OTA diagnostics helpers kept behind the diagnostics API outward home."""

from __future__ import annotations

from dataclasses import dataclass

from ...const.api import PATH_QUERY_OTA_INFO, PATH_QUERY_OTA_INFO_V2
from ..ota.query_support import (
    OtaRowDedupeKey,
    RequestPayload,
    _build_rich_ota_v2_payload,
    _build_seen_ota_row_keys,
    _merge_ota_rows,
    _ota_row_dedupe_key,
)
from ..telemetry.models import OperationOutcome
from .diagnostics_api_ota_support import (
    DeviceTypeHexResolver,
    ExtractDataList,
    InvalidParamCodeChecker,
    IotRequest,
    PrimaryOtaQueryResult,
    build_ota_api_error_outcome,
    query_controller_ota_rows,
    query_ota_rows_with_payload,
    query_rich_v2_ota_rows,
    resolve_ota_query_outcome,
)
from .types import OtaInfoRow


@dataclass(frozen=True, slots=True)
class OtaQueryResult:
    """Rows plus one typed outcome for OTA diagnostics probing."""

    rows: list[OtaInfoRow]
    outcome: OperationOutcome
    error: Exception | None = None


def _merge_primary_rows(
    merged_rows: list[OtaInfoRow],
    seen_keys: set[OtaRowDedupeKey],
    rows: list[OtaInfoRow],
    *,
    error: Exception | None,
) -> bool:
    """Merge one primary endpoint result and report whether the call succeeded."""
    if error is not None:
        return False
    _merge_ota_rows(merged_rows, seen_keys, rows)
    return True


def _build_ota_query_payloads(
    *,
    to_device_type_hex: DeviceTypeHexResolver,
    device_id: str,
    device_type: int | str,
    iot_name: str | None,
    allow_rich_v2_fallback: bool,
) -> tuple[RequestPayload, RequestPayload | None]:
    """Build primary and optional rich-v2 payloads for one OTA query."""
    ota_payload: RequestPayload = {
        "deviceId": device_id,
        "deviceType": to_device_type_hex(device_type),
    }
    return ota_payload, _build_rich_ota_v2_payload(
        ota_payload,
        iot_name=iot_name,
        allow_rich_v2_fallback=allow_rich_v2_fallback,
    )


async def _query_rich_v2_fallback_rows(
    *,
    iot_request: IotRequest,
    extract_data_list: ExtractDataList,
    is_invalid_param_error_code: InvalidParamCodeChecker,
    lipro_api_error: type[Exception],
    rich_v2_payload: RequestPayload | None,
    v1_rows: list[OtaInfoRow],
    v2_rows: list[OtaInfoRow],
) -> tuple[list[OtaInfoRow], OperationOutcome | None, Exception | None, bool]:
    """Query the optional rich-v2 fallback only when the primary rows are empty."""
    if v1_rows or v2_rows or rich_v2_payload is None:
        return [], None, None, False
    rich_v2_rows, rich_v2_outcome, rich_v2_error = await query_rich_v2_ota_rows(
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        is_invalid_param_error_code=is_invalid_param_error_code,
        lipro_api_error=lipro_api_error,
        payload=rich_v2_payload,
    )
    return (
        rich_v2_rows,
        rich_v2_outcome,
        rich_v2_error,
        rich_v2_error is None and bool(rich_v2_rows),
    )


async def _query_standard_ota_rows(
    *,
    iot_request: IotRequest,
    extract_data_list: ExtractDataList,
    lipro_api_error: type[Exception],
    ota_payload: RequestPayload,
) -> tuple[list[OtaInfoRow], Exception | None, list[OtaInfoRow], Exception | None]:
    """Query the standard OTA v1/v2 endpoints with one shared payload."""
    v1_rows, v1_error = await query_ota_rows_with_payload(
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        lipro_api_error=lipro_api_error,
        path=PATH_QUERY_OTA_INFO,
        payload=ota_payload,
    )
    v2_rows, v2_error = await query_ota_rows_with_payload(
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        lipro_api_error=lipro_api_error,
        path=PATH_QUERY_OTA_INFO_V2,
        payload=ota_payload,
    )
    return v1_rows, v1_error, v2_rows, v2_error


def _resolve_primary_endpoint_state(
    *,
    v1_rows: list[OtaInfoRow],
    v1_error: Exception | None,
    v2_rows: list[OtaInfoRow],
    v2_error: Exception | None,
) -> tuple[list[OtaInfoRow], set[OtaRowDedupeKey], bool, Exception | None]:
    """Collapse v1/v2 endpoint results into one merge state."""
    merged_rows: list[OtaInfoRow] = []
    seen_keys: set[OtaRowDedupeKey] = set()
    ota_success = _merge_primary_rows(merged_rows, seen_keys, v1_rows, error=v1_error)
    ota_success = (
        _merge_primary_rows(merged_rows, seen_keys, v2_rows, error=v2_error)
        or ota_success
    )
    return merged_rows, seen_keys, ota_success, v2_error or v1_error


def _merge_rich_v2_fallback_state(
    *,
    merged_rows: list[OtaInfoRow],
    seen_keys: set[OtaRowDedupeKey],
    rich_v2_rows: list[OtaInfoRow],
    rich_v2_error: Exception | None,
    ota_success: bool,
    ota_error: Exception | None,
) -> tuple[bool, Exception | None]:
    """Merge rich-v2 fallback rows and update success/error state."""
    if rich_v2_error is not None:
        return ota_success, rich_v2_error
    if not rich_v2_rows:
        return ota_success, ota_error
    _merge_ota_rows(merged_rows, seen_keys, rich_v2_rows)
    return True, ota_error


async def _query_primary_ota_rows(
    *,
    iot_request: IotRequest,
    extract_data_list: ExtractDataList,
    is_invalid_param_error_code: InvalidParamCodeChecker,
    lipro_api_error: type[Exception],
    ota_payload: RequestPayload,
    rich_v2_payload: RequestPayload | None,
) -> PrimaryOtaQueryResult:
    """Query OTA primary endpoints and collapse their local fallback state."""
    v1_rows, v1_error, v2_rows, v2_error = await _query_standard_ota_rows(
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        lipro_api_error=lipro_api_error,
        ota_payload=ota_payload,
    )
    merged_rows, seen_keys, ota_success, ota_error = _resolve_primary_endpoint_state(
        v1_rows=v1_rows,
        v1_error=v1_error,
        v2_rows=v2_rows,
        v2_error=v2_error,
    )
    (
        rich_v2_rows,
        rich_v2_outcome,
        rich_v2_error,
        rich_v2_recovered,
    ) = await _query_rich_v2_fallback_rows(
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        is_invalid_param_error_code=is_invalid_param_error_code,
        lipro_api_error=lipro_api_error,
        rich_v2_payload=rich_v2_payload,
        v1_rows=v1_rows,
        v2_rows=v2_rows,
    )
    ota_success, ota_error = _merge_rich_v2_fallback_state(
        merged_rows=merged_rows,
        seen_keys=seen_keys,
        rich_v2_rows=rich_v2_rows,
        rich_v2_error=rich_v2_error,
        ota_success=ota_success,
        ota_error=ota_error,
    )
    return PrimaryOtaQueryResult(
        rows=merged_rows,
        error=ota_error,
        success=ota_success,
        primary_failure_recovered=(v1_error is not None or v2_error is not None)
        and ota_success,
        rich_v2_recovered=rich_v2_recovered,
        rich_v2_outcome=rich_v2_outcome,
    )


def _build_primary_failure_result(
    primary_result: PrimaryOtaQueryResult,
) -> OtaQueryResult | None:
    """Convert an unrecovered primary-endpoint failure into the outward result."""
    if primary_result.success or primary_result.error is None:
        return None
    return OtaQueryResult(
        rows=[],
        outcome=build_ota_api_error_outcome(
            primary_result.error,
            kind="failed",
            reason_code="primary_endpoints_failed",
        ),
        error=primary_result.error,
    )


async def _query_controller_rows_with_outcome(
    *,
    iot_request: IotRequest,
    extract_data_list: ExtractDataList,
    is_invalid_param_error_code: InvalidParamCodeChecker,
    lipro_api_error: type[Exception],
    merged_rows: list[OtaInfoRow],
) -> OperationOutcome | None:
    """Merge controller OTA rows and return any degraded controller outcome."""
    seen_keys = _build_seen_ota_row_keys(merged_rows)
    controller_rows, controller_outcome = await query_controller_ota_rows(
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        is_invalid_param_error_code=is_invalid_param_error_code,
        lipro_api_error=lipro_api_error,
    )
    _merge_ota_rows(merged_rows, seen_keys, controller_rows)
    return controller_outcome


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
    ota_payload, rich_v2_payload = _build_ota_query_payloads(
        to_device_type_hex=to_device_type_hex,
        device_id=device_id,
        device_type=device_type,
        iot_name=iot_name,
        allow_rich_v2_fallback=allow_rich_v2_fallback,
    )
    primary_result = await _query_primary_ota_rows(
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        is_invalid_param_error_code=is_invalid_param_error_code,
        lipro_api_error=lipro_api_error,
        ota_payload=ota_payload,
        rich_v2_payload=rich_v2_payload,
    )
    if failure_result := _build_primary_failure_result(primary_result):
        return failure_result

    merged_rows = list(primary_result.rows)
    controller_outcome = await _query_controller_rows_with_outcome(
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        is_invalid_param_error_code=is_invalid_param_error_code,
        lipro_api_error=lipro_api_error,
        merged_rows=merged_rows,
    )
    return OtaQueryResult(
        rows=merged_rows,
        outcome=resolve_ota_query_outcome(
            primary_failure_recovered=primary_result.primary_failure_recovered,
            rich_v2_recovered=primary_result.rich_v2_recovered,
            rich_v2_outcome=primary_result.rich_v2_outcome,
            controller_outcome=controller_outcome,
        ),
    )


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


__all__ = [
    "OtaQueryResult",
    "_build_rich_ota_v2_payload",
    "_merge_ota_rows",
    "_ota_row_dedupe_key",
    "query_ota_info",
    "query_ota_info_with_outcome",
]
