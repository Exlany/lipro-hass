"""OTA diagnostics helpers kept behind the diagnostics API outward home."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
import logging

from ...const.api import (
    PATH_QUERY_CONTROLLER_OTA,
    PATH_QUERY_OTA_INFO,
    PATH_QUERY_OTA_INFO_V2,
)
from ..ota.query_support import (
    OtaRowDedupeKey,
    RequestPayload,
    _build_rich_ota_v2_payload,
    _build_seen_ota_row_keys,
    _merge_ota_rows,
    _ota_row_dedupe_key,
    _valid_ota_rows,
)
from ..telemetry.models import (
    OperationOutcome,
    OutcomeKind,
    build_operation_outcome,
    build_operation_outcome_from_exception,
)
from ..utils.log_safety import safe_error_placeholder
from .types import JsonValue, OtaInfoRow

_LOGGER = logging.getLogger(__name__)

IotRequest = Callable[..., Awaitable[JsonValue]]
ExtractDataList = Callable[[object], Sequence[object]]
DeviceTypeHexResolver = Callable[[int | str], str]
InvalidParamCodeChecker = Callable[[object], bool]

_OTA_FAILURE_ORIGIN = "diagnostics.query_ota_info"


@dataclass(frozen=True, slots=True)
class OtaQueryResult:
    """Rows plus one typed outcome for OTA diagnostics probing."""

    rows: list[OtaInfoRow]
    outcome: OperationOutcome
    error: Exception | None = None


@dataclass(frozen=True, slots=True)
class _PrimaryOtaQueryResult:
    """Primary OTA probes plus the fallback outcome signals they produced."""

    rows: list[OtaInfoRow]
    error: Exception | None
    success: bool
    primary_failure_recovered: bool
    rich_v2_recovered: bool
    rich_v2_outcome: OperationOutcome | None


def _extract_http_status_from_error(err: Exception) -> int | None:
    code = getattr(err, "code", None)
    return code if isinstance(code, int) else None


def _api_error_outcome(
    err: Exception,
    *,
    kind: OutcomeKind,
    reason_code: str,
) -> OperationOutcome:
    return build_operation_outcome_from_exception(
        err,
        kind=kind,
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
    preferred_outcome = _first_ota_outcome(
        build_operation_outcome(
            kind="degraded",
            reason_code="primary_endpoint_recovered",
        )
        if primary_failure_recovered
        else None,
        build_operation_outcome(
            kind="degraded",
            reason_code="rich_v2_recovered",
        )
        if rich_v2_recovered
        else None,
        rich_v2_outcome,
        controller_outcome,
    )
    if preferred_outcome is not None:
        return preferred_outcome
    return build_operation_outcome(kind="success", reason_code="ota_query_complete")


def _first_ota_outcome(*outcomes: OperationOutcome | None) -> OperationOutcome | None:
    """Return the first non-empty OTA outcome in precedence order."""
    for outcome in outcomes:
        if outcome is not None:
            return outcome
    return None


async def _query_ota_rows(
    *,
    iot_request: IotRequest,
    extract_data_list: ExtractDataList,
    lipro_api_error: type[Exception],
    path: str,
    payload: RequestPayload,
) -> tuple[list[OtaInfoRow], Exception | None]:
    """Query one OTA endpoint and normalize rows plus terminal error."""
    try:
        result = await iot_request(path, payload)
    except lipro_api_error as err:
        _LOGGER.debug(
            "OTA endpoint %s failed (%s)",
            path,
            safe_error_placeholder(err),
        )
        return [], err
    return _valid_ota_rows(extract_data_list(result)), None


async def _query_rich_v2_ota_rows(
    *,
    iot_request: IotRequest,
    extract_data_list: ExtractDataList,
    is_invalid_param_error_code: InvalidParamCodeChecker,
    lipro_api_error: type[Exception],
    payload: RequestPayload,
) -> tuple[list[OtaInfoRow], OperationOutcome | None, Exception | None]:
    """Query the richer OTA v2 payload and classify degraded outcomes."""
    try:
        result = await iot_request(PATH_QUERY_OTA_INFO_V2, payload)
    except lipro_api_error as err:
        code = getattr(err, "code", None)
        if is_invalid_param_error_code(code):
            _LOGGER.debug(
                "OTA endpoint %s rejected richer payload (code=%s, err=%s)",
                PATH_QUERY_OTA_INFO_V2,
                code,
                safe_error_placeholder(err),
            )
            return [], _api_error_outcome(
                err,
                kind="degraded",
                reason_code="rich_v2_invalid_param",
            ), err

        _LOGGER.debug(
            "OTA endpoint %s richer payload failed (%s)",
            PATH_QUERY_OTA_INFO_V2,
            safe_error_placeholder(err),
        )
        return [], _api_error_outcome(
            err,
            kind="degraded",
            reason_code="rich_v2_failed",
        ), err

    return _valid_ota_rows(extract_data_list(result)), None, None


async def _query_controller_ota_rows(
    *,
    iot_request: IotRequest,
    extract_data_list: ExtractDataList,
    is_invalid_param_error_code: InvalidParamCodeChecker,
    lipro_api_error: type[Exception],
) -> tuple[list[OtaInfoRow], OperationOutcome | None]:
    """Query controller OTA rows and classify degraded fallback outcomes."""
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
            return [], _api_error_outcome(
                err,
                kind="degraded",
                reason_code="controller_invalid_param",
            )

        _LOGGER.debug(
            "Controller OTA endpoint %s failed (%s)",
            PATH_QUERY_CONTROLLER_OTA,
            safe_error_placeholder(err),
        )
        return [], _api_error_outcome(
            err,
            kind="degraded",
            reason_code="controller_failed",
        )

    return _valid_ota_rows(extract_data_list(controller_result)), None


async def _query_primary_ota_rows(
    *,
    iot_request: IotRequest,
    extract_data_list: ExtractDataList,
    is_invalid_param_error_code: InvalidParamCodeChecker,
    lipro_api_error: type[Exception],
    ota_payload: RequestPayload,
    rich_v2_payload: RequestPayload | None,
) -> _PrimaryOtaQueryResult:
    """Query OTA primary endpoints and collapse their local fallback state."""
    merged_rows: list[OtaInfoRow] = []
    seen_keys: set[OtaRowDedupeKey] = set()
    ota_error: Exception | None = None
    ota_success = False
    v1_failed = False
    v2_failed = False
    rich_v2_recovered = False
    rich_v2_outcome: OperationOutcome | None = None

    v1_rows, v1_error = await _query_ota_rows(
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        lipro_api_error=lipro_api_error,
        path=PATH_QUERY_OTA_INFO,
        payload=ota_payload,
    )
    if v1_error is not None:
        ota_error = v1_error
        v1_failed = True
    else:
        _merge_ota_rows(merged_rows, seen_keys, v1_rows)
        ota_success = True

    v2_rows, v2_error = await _query_ota_rows(
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        lipro_api_error=lipro_api_error,
        path=PATH_QUERY_OTA_INFO_V2,
        payload=ota_payload,
    )
    if v2_error is not None:
        ota_error = v2_error
        v2_failed = True
    else:
        ota_success = True
        _merge_ota_rows(merged_rows, seen_keys, v2_rows)
        if not v1_rows and not v2_rows and rich_v2_payload is not None:
            rich_v2_rows, rich_v2_outcome, rich_v2_error = await _query_rich_v2_ota_rows(
                iot_request=iot_request,
                extract_data_list=extract_data_list,
                is_invalid_param_error_code=is_invalid_param_error_code,
                lipro_api_error=lipro_api_error,
                payload=rich_v2_payload,
            )
            if rich_v2_error is None:
                ota_success = True
                _merge_ota_rows(merged_rows, seen_keys, rich_v2_rows)
                rich_v2_recovered = bool(rich_v2_rows)
            else:
                ota_error = rich_v2_error

    return _PrimaryOtaQueryResult(
        rows=merged_rows,
        error=ota_error,
        success=ota_success,
        primary_failure_recovered=(v1_failed or v2_failed) and ota_success,
        rich_v2_recovered=rich_v2_recovered,
        rich_v2_outcome=rich_v2_outcome,
    )


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

    primary_result = await _query_primary_ota_rows(
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        is_invalid_param_error_code=is_invalid_param_error_code,
        lipro_api_error=lipro_api_error,
        ota_payload=ota_payload,
        rich_v2_payload=rich_v2_payload,
    )

    if not primary_result.success and primary_result.error is not None:
        return OtaQueryResult(
            rows=[],
            outcome=_api_error_outcome(
                primary_result.error,
                kind="failed",
                reason_code="primary_endpoints_failed",
            ),
            error=primary_result.error,
        )

    merged_rows = list(primary_result.rows)
    seen_keys = _build_seen_ota_row_keys(merged_rows)
    controller_rows, controller_outcome = await _query_controller_ota_rows(
        iot_request=iot_request,
        extract_data_list=extract_data_list,
        is_invalid_param_error_code=is_invalid_param_error_code,
        lipro_api_error=lipro_api_error,
    )
    _merge_ota_rows(merged_rows, seen_keys, controller_rows)

    outcome = _resolve_ota_query_outcome(
        primary_failure_recovered=primary_result.primary_failure_recovered,
        rich_v2_recovered=primary_result.rich_v2_recovered,
        rich_v2_outcome=primary_result.rich_v2_outcome,
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


__all__ = [
    "OtaQueryResult",
    "_build_rich_ota_v2_payload",
    "_merge_ota_rows",
    "_ota_row_dedupe_key",
    "query_ota_info",
    "query_ota_info_with_outcome",
]
