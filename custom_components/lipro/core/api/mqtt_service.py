"""MQTT endpoint helpers for Lipro API client."""

from __future__ import annotations

from typing import Any, cast


async def get_mqtt_config(
    *,
    request_iot_mapping: Any,
    is_success_code: Any,
    unwrap_iot_success_payload: Any,
    require_mapping_response: Any,
    lipro_api_error: type[Exception],
    path_get_mqtt_config: str,
    is_retry: bool = False,
    retry_count: int = 0,
) -> dict[str, Any]:
    """Get MQTT configuration for real-time status updates."""
    result, _ = await request_iot_mapping(
        path_get_mqtt_config,
        {},
        is_retry=is_retry,
        retry_count=retry_count,
    )

    # Endpoint may return {"accessKey": "...", "secretKey": "..."} directly.
    if "accessKey" in result and "secretKey" in result:
        return cast(dict[str, Any], result)

    # Fallback: if backend wraps payload in standard response envelope.
    code = result.get("code")
    if is_success_code(code):
        payload = unwrap_iot_success_payload(result)
        return cast(
            dict[str, Any],
            require_mapping_response(path_get_mqtt_config, payload),
        )

    message = result.get("message", "Unknown error")
    raise lipro_api_error(message, code)
