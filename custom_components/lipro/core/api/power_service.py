"""Power endpoint helpers for Lipro API client."""

from __future__ import annotations

from typing import Any, cast

OutletPowerInfoPayload = dict[str, Any] | list[dict[str, Any]]


async def fetch_outlet_power_info(
    *,
    device_ids: list[str],
    sanitize_iot_device_ids: Any,
    iot_request: Any,
    require_mapping_response: Any,
    is_invalid_param_error_code: Any,
    lipro_api_error: type[Exception],
    logger: Any,
    path_query_outlet_power: str,
) -> OutletPowerInfoPayload:
    """Fetch power information for outlet devices."""
    sanitized_ids = sanitize_iot_device_ids(
        device_ids,
        endpoint=path_query_outlet_power,
    )
    if not sanitized_ids:
        return {}

    try:
        result = await iot_request(
            path_query_outlet_power,
            {"deviceIds": sanitized_ids},
        )
        if isinstance(result, list):
            rows = [row for row in result if isinstance(row, dict)]
            if len(rows) != len(result):
                logger.debug(
                    "Power-info payload dropped %d non-mapping rows",
                    len(result) - len(rows),
                )
            return rows
        if isinstance(result, dict):
            return cast(
                dict[str, Any],
                require_mapping_response(path_query_outlet_power, result),
            )
        logger.debug(
            "Power-info payload returned unexpected type (%s), treating as empty",
            type(result).__name__,
        )
        return {}
    except lipro_api_error as err:
        # Keep behavior: invalid-param business error should degrade to empty payload.
        code = getattr(err, "code", None)
        if is_invalid_param_error_code(code):
            logger.debug(
                "Power-info endpoint rejected device IDs (count=%d, code=%s), treating as empty",
                len(sanitized_ids),
                code,
            )
            return {}
        raise
