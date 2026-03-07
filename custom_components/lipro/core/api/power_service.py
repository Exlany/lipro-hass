"""Power endpoint helpers for Lipro API client."""

from __future__ import annotations

from typing import Any, cast

OutletPowerInfoPayload = dict[str, Any]


async def fetch_outlet_power_info(
    *,
    device_id: str,
    normalize_power_target_id: Any,
    iot_request: Any,
    require_mapping_response: Any,
    is_invalid_param_error_code: Any,
    lipro_api_error: type[Exception],
    logger: Any,
    path_query_outlet_power: str,
) -> OutletPowerInfoPayload:
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
        return cast(
            dict[str, Any],
            require_mapping_response(path_query_outlet_power, result),
        )

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
        return rows[0] if len(rows) == 1 else {"data": rows}

    logger.debug(
        "Power-info payload returned unexpected type (%s) for %s, skipping",
        type(result).__name__,
        normalized_target_id,
    )
    return {}
