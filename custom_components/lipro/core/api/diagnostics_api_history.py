"""Sensor-history diagnostics helpers kept behind the diagnostics API outward home."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from ...const.api import PATH_FETCH_BODY_SENSOR_HISTORY, PATH_FETCH_DOOR_SENSOR_HISTORY
from .types import JsonObject, JsonValue

ResponseMapping = JsonObject
IotRequest = Callable[..., Awaitable[JsonValue]]
RequireMappingResponse = Callable[[str, object], JsonObject]
DeviceTypeHexResolver = Callable[[int | str], str]


async def fetch_body_sensor_history(
    *,
    iot_request: IotRequest,
    require_mapping_response: RequireMappingResponse,
    to_device_type_hex: DeviceTypeHexResolver,
    device_id: str,
    device_type: int | str,
    sensor_device_id: str,
    mesh_type: str,
) -> ResponseMapping:
    """Fetch body sensor history snapshot for diagnostics."""
    return await fetch_sensor_history(
        iot_request=iot_request,
        require_mapping_response=require_mapping_response,
        to_device_type_hex=to_device_type_hex,
        path=PATH_FETCH_BODY_SENSOR_HISTORY,
        device_id=device_id,
        device_type=device_type,
        sensor_device_id=sensor_device_id,
        mesh_type=mesh_type,
    )


async def fetch_door_sensor_history(
    *,
    iot_request: IotRequest,
    require_mapping_response: RequireMappingResponse,
    to_device_type_hex: DeviceTypeHexResolver,
    device_id: str,
    device_type: int | str,
    sensor_device_id: str,
    mesh_type: str,
) -> ResponseMapping:
    """Fetch door sensor history snapshot for diagnostics."""
    return await fetch_sensor_history(
        iot_request=iot_request,
        require_mapping_response=require_mapping_response,
        to_device_type_hex=to_device_type_hex,
        path=PATH_FETCH_DOOR_SENSOR_HISTORY,
        device_id=device_id,
        device_type=device_type,
        sensor_device_id=sensor_device_id,
        mesh_type=mesh_type,
    )


async def fetch_sensor_history(
    *,
    iot_request: IotRequest,
    require_mapping_response: RequireMappingResponse,
    to_device_type_hex: DeviceTypeHexResolver,
    path: str,
    device_id: str,
    device_type: int | str,
    sensor_device_id: str,
    mesh_type: str,
) -> ResponseMapping:
    """Fetch one sensor-history payload using shared request fields."""
    result = await iot_request(
        path,
        {
            "deviceId": device_id,
            "deviceType": to_device_type_hex(device_type),
            "sensorDeviceId": sensor_device_id,
            "meshType": mesh_type,
        },
    )
    return require_mapping_response(path, result)


__all__ = [
    "fetch_body_sensor_history",
    "fetch_door_sensor_history",
    "fetch_sensor_history",
]
