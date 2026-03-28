"""Type definitions for coordinator module.

This module provides explicit type definitions to reduce dynamic payload usage and
keep runtime/shared telemetry contracts machine-checkable.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Literal, TypedDict

from ..api.types import JsonValue
from ..command.result_policy import TracePayload

# Property value types

type PropertyScalar = int | float | str | bool | None
"""Type alias for scalar device property values."""


type PropertyValue = JsonValue
"""Type alias for device property payload values."""


type PropertyDict = dict[str, PropertyValue]
"""Type alias for device property dictionaries."""


# Command types
class CommandPayload(TypedDict, total=False):
    """Command payload structure for device control."""

    action: str
    properties: list[dict[str, str]]
    device_id: str


type CommandTrace = TracePayload
"""Canonical command execution trace payload."""


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


type MetricMapping = dict[str, object]
"""Shared narrow mapping used by runtime metrics / telemetry sections."""


# Metrics and runtime types
class RuntimeMetrics(TypedDict, total=False):
    """Runtime metrics payload exported by composed runtimes."""

    algorithm: MetricMapping
    metrics: MetricMapping
    adjuster: MetricMapping
    scheduler: MetricMapping
    strategy: MetricMapping
    command_count: int
    success_rate: float
    last_failure: CommandFailureSummary | None
    debug_enabled: bool
    trace_count: int
    confirmation: MetricMapping
    has_transport: bool
    is_connected: bool
    disconnect_time: float | None
    disconnect_notified: bool
    last_transport_error: str | None
    last_transport_error_stage: str | None
    failure_summary: MetricMapping
    backoff_gate_logged: bool
    device_count: int
    online_count: int
    update_count: int


class ConnectStateEvent(TypedDict):
    """One connect-state observation recorded by runtime telemetry."""

    device_serial: str
    timestamp: float
    is_online: bool


class GroupReconciliationRequestEvent(TypedDict):
    """One group-reconciliation signal recorded by runtime telemetry."""

    device_name: str
    timestamp: float


class RuntimeSignalsSnapshot(TypedDict):
    """Signals section of runtime telemetry snapshot."""

    connect_state_event_count: int
    group_reconciliation_request_count: int
    recent_connect_state_events: list[ConnectStateEvent]
    recent_group_reconciliation_requests: list[GroupReconciliationRequestEvent]


class RuntimeTelemetrySnapshot(TypedDict, total=False):
    """Stable runtime telemetry snapshot exposed to control-plane consumers."""

    device_count: int
    polling_interval_seconds: int | None
    failure_summary: MetricMapping
    last_runtime_failure_stage: str | None
    mqtt: MetricMapping
    command: RuntimeMetrics
    status: RuntimeMetrics
    tuning: RuntimeMetrics
    signals: RuntimeSignalsSnapshot
    recent_command_traces: list[CommandTrace]


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
    "ConnectStateEvent",
    "DeviceApiData",
    "DeviceFilter",
    "DeviceKeyNormalizer",
    "DeviceUpdateCallback",
    "GroupReconciliationRequestEvent",
    "MetricMapping",
    "MqttCredentials",
    "MqttMessage",
    "OutletPowerData",
    "PropertyDict",
    "PropertyUpdateCallback",
    "PropertyValue",
    "ReauthCallback",
    "RefreshStrategy",
    "RuntimeMetrics",
    "RuntimeSignalsSnapshot",
    "RuntimeTelemetrySnapshot",
    "StatusQueryMetrics",
    "TuningMetrics",
]
