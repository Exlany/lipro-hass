"""Power endpoint helpers for Lipro API client."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging

from .types import JsonObject

type OutletPowerInfoRow = JsonObject
type OutletPowerInfoResult = OutletPowerInfoRow | list[OutletPowerInfoRow]
type NormalizePowerTargetId = Callable[[str], str | None]
type IoTRequest = Callable[[str, JsonObject], Awaitable[object]]
type RequireMappingResponse = Callable[[str, object], OutletPowerInfoRow]
type IsInvalidParamErrorCode = Callable[[object], bool]


def _normalize_power_list_payload(
    *,
    result: list[object],
    normalized_target_id: str,
    logger: logging.Logger,
) -> OutletPowerInfoResult:
    rows = [row for row in result if isinstance(row, dict)]
    if len(rows) != len(result):
        logger.debug(
            "Power-info payload dropped %d non-mapping rows for %s",
            len(result) - len(rows),
            normalized_target_id,
        )
    if not rows:
        return {}
    if len(rows) == 1:
        return dict(rows[0])
    return [dict(row) for row in rows]


def _normalize_power_payload(
    *,
    result: object,
    path_query_outlet_power: str,
    normalized_target_id: str,
    require_mapping_response: RequireMappingResponse,
    logger: logging.Logger,
) -> OutletPowerInfoResult:
    if isinstance(result, dict):
        return require_mapping_response(path_query_outlet_power, result)

    if isinstance(result, list):
        return _normalize_power_list_payload(
            result=result,
            normalized_target_id=normalized_target_id,
            logger=logger,
        )

    logger.debug(
        "Power-info payload returned unexpected type (%s) for %s, skipping",
        type(result).__name__,
        normalized_target_id,
    )
    return {}


def _is_invalid_power_target_error(
    *,
    err: Exception,
    is_invalid_param_error_code: IsInvalidParamErrorCode,
) -> bool:
    return is_invalid_param_error_code(getattr(err, "code", None))


async def fetch_outlet_power_info(
    *,
    device_id: str,
    normalize_power_target_id: NormalizePowerTargetId,
    iot_request: IoTRequest,
    require_mapping_response: RequireMappingResponse,
    is_invalid_param_error_code: IsInvalidParamErrorCode,
    lipro_api_error: type[Exception],
    logger: logging.Logger,
    path_query_outlet_power: str,
) -> OutletPowerInfoResult:
    """Fetch power information for one outlet-power target."""
    normalized_target_id = normalize_power_target_id(device_id)
    if normalized_target_id is None:
        return {}

    try:
        result = await iot_request(
            path_query_outlet_power,
            {"deviceId": normalized_target_id},
        )
    except lipro_api_error as err:
        if _is_invalid_power_target_error(
            err=err,
            is_invalid_param_error_code=is_invalid_param_error_code,
        ):
            logger.debug(
                "Power-info endpoint rejected deviceId=%s (code=%s), skipping",
                normalized_target_id,
                getattr(err, "code", None),
            )
            return {}
        raise

    return _normalize_power_payload(
        result=result,
        path_query_outlet_power=path_query_outlet_power,
        normalized_target_id=normalized_target_id,
        require_mapping_response=require_mapping_response,
        logger=logger,
    )
