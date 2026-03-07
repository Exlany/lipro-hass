"""Power endpoint helpers for Lipro API client."""

from __future__ import annotations

from typing import Any, cast

OutletPowerInfoPayload = dict[str, Any]


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

    aggregated_payload: dict[str, Any] = {}
    single_device_request = len(sanitized_ids) == 1

    for device_id in sanitized_ids:
        try:
            result = await iot_request(
                path_query_outlet_power,
                {"deviceId": device_id},
            )
        except lipro_api_error as err:
            code = getattr(err, "code", None)
            if is_invalid_param_error_code(code):
                logger.debug(
                    "Power-info endpoint rejected deviceId=%s (code=%s), skipping",
                    device_id,
                    code,
                )
                continue
            raise

        if isinstance(result, dict):
            payload = cast(
                dict[str, Any],
                require_mapping_response(path_query_outlet_power, result),
            )
            if single_device_request:
                return payload
            aggregated_payload[device_id] = payload
            continue

        if isinstance(result, list):
            rows = [row for row in result if isinstance(row, dict)]
            if len(rows) != len(result):
                logger.debug(
                    "Power-info payload dropped %d non-mapping rows for %s",
                    len(result) - len(rows),
                    device_id,
                )
            if not rows:
                continue
            payload = rows[0] if len(rows) == 1 else {"data": rows}
            if single_device_request:
                return payload
            aggregated_payload[device_id] = payload
            continue

        logger.debug(
            "Power-info payload returned unexpected type (%s) for %s, skipping",
            type(result).__name__,
            device_id,
        )

    return aggregated_payload
