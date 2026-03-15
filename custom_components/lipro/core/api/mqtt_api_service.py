"""MQTT endpoint helpers for Lipro API client."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

type MappingPayload = dict[str, object]
type RequestIotMapping = Callable[..., Awaitable[tuple[object, str | None]]]
type IsSuccessCode = Callable[[object], bool]
type UnwrapIoTSuccessPayload = Callable[[MappingPayload], object]
type RequireMappingResponse = Callable[[str, object], object]


def _extract_mqtt_config_payload(
    result: object,
    *,
    is_success_code: IsSuccessCode,
) -> MappingPayload | None:
    """Decode MQTT config through the same canonical shape without importing protocol."""
    if not isinstance(result, dict):
        return None

    if "accessKey" in result and "secretKey" in result:
        return dict(result)

    payload = result.get("data")
    if not isinstance(payload, dict):
        return None
    if "accessKey" not in payload or "secretKey" not in payload:
        return None
    if "code" not in result or is_success_code(result.get("code")):
        return dict(payload)
    return None


async def get_mqtt_config(
    *,
    request_iot_mapping: RequestIotMapping,
    is_success_code: IsSuccessCode,
    unwrap_iot_success_payload: UnwrapIoTSuccessPayload,
    require_mapping_response: RequireMappingResponse,
    lipro_api_error: type[Exception],
    path_get_mqtt_config: str,
    is_retry: bool = False,
    retry_count: int = 0,
) -> MappingPayload:
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
        wrapped_payload = require_mapping_response(
            path_get_mqtt_config,
            unwrap_iot_success_payload(result),
        )
        if isinstance(wrapped_payload, dict):
            mapping_payload = dict(wrapped_payload)
            if "accessKey" in mapping_payload and "secretKey" in mapping_payload:
                return mapping_payload

    if isinstance(result, dict):
        raise lipro_api_error(
            result.get("message", "MQTT config response missing accessKey/secretKey"),
            result.get("code"),
        )
    raise lipro_api_error("MQTT config response missing accessKey/secretKey")
