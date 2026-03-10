"""Typed API payload contracts used by Lipro client helpers."""

from __future__ import annotations

from typing import Any, TypedDict

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


class ApiResponse(TypedDict, total=False):
    """Base API response structure."""

    code: int
    msg: str
    data: Any


class LoginResponse(TypedDict):
    """Login API response data."""

    access_token: str
    refresh_token: str
    expires_in: int
    user_id: str


class DeviceListItem(TypedDict, total=False):
    """Device list item structure."""

    serial: str
    deviceId: str
    iotDeviceId: str
    name: str
    deviceType: int
    online: bool
    properties: dict[str, Any]


class DeviceListResponse(TypedDict):
    """Device list API response data."""

    devices: list[DeviceListItem]
    total: int


class DeviceStatusItem(TypedDict, total=False):
    """Device status item structure."""

    iotId: str
    properties: dict[str, Any]


class MqttConfigResponse(TypedDict, total=False):
    """MQTT config API response data."""

    accessKey: str
    secretKey: str
    endpoint: str
    port: int


class DevicePropertyRow(TypedDict, total=False):
    """One raw property item returned by device APIs."""

    key: str
    value: JsonValue


class DeviceApiResponse(TypedDict, total=False):
    """Normalized device payload returned by device-list endpoints."""

    deviceId: str | int
    serial: str
    deviceName: str
    type: int | str
    iotName: str
    roomId: str | int
    roomName: str
    productId: str | int
    physicalModel: str
    properties: list[DevicePropertyRow]


class CommandResultApiResponse(TypedDict, total=False):
    """Normalized payload returned by command-result endpoints."""

    code: str | int
    message: str
    success: bool
    msgSn: str
    pushSuccess: bool
    pushTimestamp: str | int


class ScheduleTimingRow(TypedDict, total=False):
    """One normalized schedule timing row."""

    id: str | int
    timingId: str | int
    hour: int
    minute: int
    enable: bool | int | str
    repeat: str
    actionType: str | int
    actionData: str
    deviceId: str
    scheduleJson: str
    schedule: dict[str, list[int]]
    active: bool


class ScheduleApiResponse(TypedDict, total=False):
    """Normalized schedule payload."""

    code: str | int
    message: str
    success: bool
    data: list[ScheduleTimingRow]


class OtaInfoRow(TypedDict, total=False):
    """One normalized OTA metadata row."""

    deviceId: str
    iotId: str
    deviceType: str
    bleName: str
    productName: str
    latestVersion: str
    firmwareVersion: str
    version: str
    firmwareUrl: str
    url: str
    md5: str


class DiagnosticsApiResponse(TypedDict, total=False):
    """Common response payload for diagnostics/history queries."""

    code: str | int
    message: str
    success: bool
    data: list[dict[str, JsonValue]] | dict[str, JsonValue]


__all__ = [
    "ApiResponse",
    "CommandResultApiResponse",
    "DeviceApiResponse",
    "DeviceListItem",
    "DeviceListResponse",
    "DevicePropertyRow",
    "DeviceStatusItem",
    "DiagnosticsApiResponse",
    "JsonObject",
    "JsonScalar",
    "JsonValue",
    "LoginResponse",
    "MqttConfigResponse",
    "OtaInfoRow",
    "ScheduleApiResponse",
    "ScheduleTimingRow",
]
