"""Type definitions for API responses."""

from __future__ import annotations

from typing import Any, TypedDict


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


__all__ = [
    "ApiResponse",
    "DeviceListItem",
    "DeviceListResponse",
    "DeviceStatusItem",
    "LoginResponse",
    "MqttConfigResponse",
]
