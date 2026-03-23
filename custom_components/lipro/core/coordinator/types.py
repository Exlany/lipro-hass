"""Type definitions for coordinator module.

This module provides explicit type definitions to reduce Any usage and improve
type safety across the coordinator components.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Literal, TypedDict

# Property value types
type PropertyScalar = int | float | str | bool | None
"""Type alias for scalar device property values."""

type PropertyValue = PropertyScalar | list[Any] | dict[str, Any]
"""Type alias for device property payload values."""

type PropertyDict = dict[str, PropertyValue]
"""Type alias for device property dictionaries."""


# Command types
class CommandPayload(TypedDict, total=False):
    """Command payload structure for device control."""

    action: str
    properties: list[dict[str, str]]
    device_id: str


type CommandTrace = dict[str, Any]
"""Command execution trace payload (debug/diagnostics).

The trace payload is built incrementally during command execution and is
intentionally modeled as a free-form dictionary to avoid tight coupling
between coordinator runtimes and the lower-level command helpers.
"""


type CommandFailureCategory = Literal["auth", "protocol", "runtime", "unexpected"]
"""Normalized command-failure category exposed to runtime/control consumers."""


type CommandReauthReason = Literal["auth_expired", "auth_error"]
"""Canonical reauthentication reasons surfaced by command arbitration."""


class CommandFailureSummary(TypedDict, total=False):
    """Normalized command failure details exposed to coordinator consumers."""

    reason: str
    code: int | str
    route: str
    device_id: str
    message: str
    error_type: str
    failure_category: CommandFailureCategory
    reauth_reason: CommandReauthReason


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
type DeviceUpdateCallback = Callable[[], None]
"""Callback for device state updates."""

type PropertyUpdateCallback = Callable[[str, PropertyDict], Awaitable[None] | None]
"""Callback for property updates with device_id and properties."""

type ReauthCallback = Callable[[str], Awaitable[None]]
"""Callback for triggering reauthentication with reason."""

# Normalization function types
type DeviceKeyNormalizer = Callable[[str], str]
"""Function to normalize device identifiers to serial strings."""


# Metrics and runtime types
class RuntimeMetrics(TypedDict, total=False):
    """Runtime metrics payload exported by composed runtimes.

    Structure varies by runtime type:
    - TuningRuntime: algorithm, metrics, adjuster
    - CommandRuntime: command_count, success_rate, last_failure
    - StateRuntime: device_count, online_count, update_count
    """

    # TuningRuntime metrics
    algorithm: dict[str, Any]
    metrics: dict[str, Any]
    adjuster: dict[str, Any]

    # CommandRuntime metrics
    command_count: int
    success_rate: float
    last_failure: CommandFailureSummary | None

    # StateRuntime metrics
    device_count: int
    online_count: int
    update_count: int

    # Generic extensibility
    # Allow any additional string keys for future runtime types


class TuningMetrics(TypedDict, total=False):
    """Tuning algorithm metrics."""

    current_delay: float
    success_rate: float
    adjustment_count: int
    last_adjustment_timestamp: float


class StatusQueryMetrics(TypedDict, total=False):
    """Status query execution metrics."""

    duration: float
    device_count: int
    updated_count: int
    error: str | None
    apply_errors: list[str] | None


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
    "CommandFailureCategory",
    "CommandFailureSummary",
    "CommandPayload",
    "CommandReauthReason",
    "CommandTrace",
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
    "StatusQueryMetrics",
    "TuningMetrics",
]
