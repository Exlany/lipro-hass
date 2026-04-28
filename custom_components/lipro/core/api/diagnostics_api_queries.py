"""Misc diagnostics query helpers kept behind the diagnostics API outward home."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from ...const.api import PATH_GET_CITY, PATH_QUERY_COMMAND_RESULT, PATH_QUERY_USER_CLOUD
from .types import JsonObject

ResponseMapping = JsonObject
RequestIotMapping = Callable[..., Awaitable[tuple[JsonObject, str | None]]]
RequestIotMappingRaw = Callable[..., Awaitable[tuple[JsonObject, str | None]]]
RequireMappingResponse = Callable[[str, object], JsonObject]
IotRequest = Callable[..., Awaitable[object]]
DeviceTypeHexResolver = Callable[[int | str], str]


async def query_command_result(
    *,
    request_iot_mapping: RequestIotMapping,
    require_mapping_response: RequireMappingResponse,
    to_device_type_hex: DeviceTypeHexResolver,
    msg_sn: str,
    device_id: str,
    device_type: int | str,
) -> ResponseMapping:
    """Query async command delivery result by message serial number."""
    result, _ = await request_iot_mapping(
        PATH_QUERY_COMMAND_RESULT,
        {
            "msgSn": msg_sn,
            "deviceId": device_id,
            "deviceType": to_device_type_hex(device_type),
        },
    )
    return require_mapping_response(PATH_QUERY_COMMAND_RESULT, result)


async def get_city(
    *,
    iot_request: IotRequest,
    require_mapping_response: RequireMappingResponse,
) -> ResponseMapping:
    """Get current city metadata from IoT backend."""
    result = await iot_request(PATH_GET_CITY, {})
    return require_mapping_response(PATH_GET_CITY, result)


async def query_user_cloud(
    *,
    request_iot_mapping_raw: RequestIotMappingRaw,
    require_mapping_response: RequireMappingResponse,
) -> ResponseMapping:
    """Query cloud-assistant metadata using the verified empty-string contract."""
    result, _ = await request_iot_mapping_raw(PATH_QUERY_USER_CLOUD, "")
    return require_mapping_response(PATH_QUERY_USER_CLOUD, result)


__all__ = [
    "get_city",
    "query_command_result",
    "query_user_cloud",
]
