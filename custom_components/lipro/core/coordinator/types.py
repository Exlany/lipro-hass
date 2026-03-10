"""Type definitions for coordinator module.

This module provides explicit type definitions to reduce Any usage and improve
type safety across the coordinator components.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeAlias, TypedDict

# Property value types
PropertyValue: TypeAlias = int | str | bool | None
"""Type alias for device property values."""

PropertyDict: TypeAlias = dict[str, PropertyValue]
"""Type alias for device property dictionaries."""


# Command types
class CommandPayload(TypedDict, total=False):
    """Command payload structure for device control."""

    action: str
    properties: list[dict[str, str]]
    device_id: str


class CommandTrace(TypedDict, total=False):
    """Command execution trace information."""

    device_serial: str
    command: str
    route: str
    start_time: float
    end_time: float
    duration_ms: float
    msg_sn: str | None
    success: bool
    error: str | None
    retry_count: int
    adaptive_delay_seconds: float
    skip_immediate_refresh: bool


# MQTT types
class MqttCredentials(TypedDict):
    """MQTT connection credentials."""

    host: str
    port: int
    username: str
    password: str
    client_id: str


class MqttMessage(TypedDict):
    """MQTT message structure."""

    topic: str
    payload: dict[str, PropertyValue]
    qos: int
    retain: bool


# Device data types
class DeviceApiData(TypedDict, total=False):
    """Raw device data from API response."""

    deviceNumber: int
    serial: str
    name: str
    deviceType: int
    iotName: str
    roomId: int | None
    roomName: str | None
    isGroup: bool
    productId: int | None
    physicalModel: str | None
    properties: dict[str, PropertyValue]


# API response types
class ApiErrorResponse(TypedDict):
    """API error response structure."""

    code: int
    message: str
    data: dict[str, PropertyValue] | None


class ApiSuccessResponse(TypedDict):
    """API success response structure."""

    code: int
    message: str
    data: dict[str, PropertyValue]


# Callback types
DeviceUpdateCallback: TypeAlias = Callable[[], None]
"""Callback for device state updates."""

PropertyUpdateCallback: TypeAlias = Callable[
    [str, PropertyDict], Awaitable[None] | None
]
"""Callback for property updates with device_id and properties."""

ReauthCallback: TypeAlias = Callable[[str], Awaitable[None]]
"""Callback for triggering reauthentication with reason."""

# Normalization function types
DeviceKeyNormalizer: TypeAlias = Callable[[object], str | None]
"""Function to normalize device identifiers to serial strings."""

ConnectStatusRefreshSetter: TypeAlias = Callable[[str, bool], None]
"""Function to set connect status refresh flag for a device."""

# Metrics and runtime types
class RuntimeMetrics(TypedDict, total=False):
    """Runtime performance metrics."""

    total_commands: int
    successful_commands: int
    failed_commands: int
    average_latency_ms: float
    mqtt_messages_received: int
    device_refresh_count: int
    last_refresh_timestamp: float


class TuningMetrics(TypedDict, total=False):
    """Tuning algorithm metrics."""

    current_delay: float
    success_rate: float
    adjustment_count: int
    last_adjustment_timestamp: float


# Filter and validation types
class DeviceFilter(TypedDict, total=False):
    """Device filtering criteria."""

    device_type: int | None
    room_id: int | None
    is_group: bool | None
    has_valid_iot_id: bool | None


# Outlet power types
class OutletPowerData(TypedDict):
    """Outlet power consumption data."""

    device_id: str
    power: float
    voltage: float
    current: float
    timestamp: float


# Status refresh types
class RefreshStrategy(TypedDict):
    """Device refresh strategy configuration."""

    interval: float
    batch_size: int
    priority_devices: list[str]


__all__ = [
    "ApiErrorResponse",
    "ApiSuccessResponse",
    "CommandPayload",
    "CommandTrace",
    "ConnectStatusRefreshSetter",
    "DeviceApiData",
    "DeviceFilter",
    "DeviceKeyNormalizer",
    "DeviceUpdateCallback",
    "MqttCredentials",
    "MqttMessage",
    "OutletPowerData",
    "PropertyDict",
    "PropertyUpdateCallback",
    "PropertyValue",
    "ReauthCallback",
    "RefreshStrategy",
    "RuntimeMetrics",
    "TuningMetrics",
]
