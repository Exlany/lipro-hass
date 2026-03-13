"""MQTT endpoint helpers for Lipro API client."""

from __future__ import annotations

from functools import lru_cache
from importlib import import_module
from typing import Any, cast


@lru_cache(maxsize=1)
def _boundary_decoder_module() -> Any:
    """Resolve the protocol-boundary module lazily to avoid import cycles."""
    return import_module("custom_components.lipro.core.protocol.boundary")


def _extract_mqtt_config_payload(
    result: Any,
    *,
    is_success_code: Any,
) -> dict[str, Any] | None:
    """Extract MQTT config through the formal boundary decoder family."""
    try:
        decoded = _boundary_decoder_module().decode_mqtt_config_payload(
            result,
            is_success_code=is_success_code,
        )
    except ValueError:
        return None
    return cast(dict[str, Any], decoded.canonical)


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
    """Get MQTT configuration with direct-contract first and wrapped fallback."""
    result, _ = await request_iot_mapping(
        path_get_mqtt_config,
        {},
        is_retry=is_retry,
        retry_count=retry_count,
    )

    payload = _extract_mqtt_config_payload(result, is_success_code=is_success_code)
    if payload is not None:
        return payload

    if isinstance(result, dict) and is_success_code(result.get("code")):
        payload = require_mapping_response(
            path_get_mqtt_config,
            unwrap_iot_success_payload(result),
        )
        if "accessKey" in payload and "secretKey" in payload:
            return cast(dict[str, Any], payload)

    if isinstance(result, dict):
        raise lipro_api_error(
            result.get("message", "MQTT config response missing accessKey/secretKey"),
            result.get("code"),
        )
    raise lipro_api_error("MQTT config response missing accessKey/secretKey")
