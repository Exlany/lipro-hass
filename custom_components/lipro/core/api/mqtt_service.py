"""MQTT endpoint helpers for Lipro API client."""

from __future__ import annotations

from typing import Any, cast


async def get_mqtt_config(
    *,
    request_iot_mapping: Any,
    lipro_api_error: type[Exception],
    path_get_mqtt_config: str,
    is_retry: bool = False,
    retry_count: int = 0,
) -> dict[str, Any]:
    """Get MQTT configuration using the verified direct credential contract."""
    result, _ = await request_iot_mapping(
        path_get_mqtt_config,
        {},
        is_retry=is_retry,
        retry_count=retry_count,
    )

    if isinstance(result, dict) and "accessKey" in result and "secretKey" in result:
        return cast(dict[str, Any], result)

    if isinstance(result, dict):
        raise lipro_api_error(
            result.get("message", "MQTT config response missing accessKey/secretKey"),
            result.get("code"),
        )
    raise lipro_api_error("MQTT config response missing accessKey/secretKey")
