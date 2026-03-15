"""Power endpoint helpers for Lipro API client."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging

type OutletPowerInfoRow = dict[str, object]
type OutletPowerInfoResult = OutletPowerInfoRow | list[OutletPowerInfoRow]
type NormalizePowerTargetId = Callable[[str], str | None]
type IoTRequest = Callable[[str, dict[str, str]], Awaitable[object]]
type RequireMappingResponse = Callable[[str, object], OutletPowerInfoRow]
type IsInvalidParamErrorCode = Callable[[object], bool]


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
        code = getattr(err, "code", None)
        if is_invalid_param_error_code(code):
            logger.debug(
                "Power-info endpoint rejected deviceId=%s (code=%s), skipping",
                normalized_target_id,
                code,
            )
            return {}
        raise

    if isinstance(result, dict):
        return require_mapping_response(path_query_outlet_power, result)

    if isinstance(result, list):
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

    logger.debug(
        "Power-info payload returned unexpected type (%s) for %s, skipping",
        type(result).__name__,
        normalized_target_id,
    )
    return {}
