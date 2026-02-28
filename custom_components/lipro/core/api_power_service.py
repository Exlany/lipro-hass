"""Power endpoint helpers for Lipro API client."""

from __future__ import annotations

from typing import Any


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
) -> dict[str, Any]:
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
        return require_mapping_response(path_query_outlet_power, result)
    except lipro_api_error as err:
        # Keep behavior: invalid-param business error should degrade to empty payload.
        if is_invalid_param_error_code(err.code):
            logger.debug(
                "Power-info endpoint rejected device IDs %s (code=%s), treating as empty",
                sanitized_ids,
                err.code,
            )
            return {}
        raise
