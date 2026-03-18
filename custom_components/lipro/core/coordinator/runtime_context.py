"""Runtime context protocol for dependency injection.

This module defines the unified dependency interface shared by all runtime components,
eliminating the need for lambda closures and setter injection.

Design principles:
- Single source of truth for runtime dependencies
- Immutable after construction (frozen dataclass)
- Protocol-based for testability
- No circular dependencies (context → runtimes, not vice versa)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from ..device import LiproDevice


class DeviceResolverProtocol(Protocol):
    """Protocol for resolving device by ID."""

    def __call__(self, device_id: str) -> LiproDevice | None:
        """Resolve device by ID."""
        ...


class PropertyApplierProtocol(Protocol):
    """Protocol for applying property updates to device."""

    async def __call__(
        self,
        device: LiproDevice,
        properties: dict[str, Any],
        source: str,
    ) -> bool:
        """Apply property updates to device."""
        ...


class ListenerNotifierProtocol(Protocol):
    """Protocol for notifying listeners of state changes."""

    def __call__(self) -> None:
        """Notify listeners that state has changed."""
        ...


class ConnectStateRecorderProtocol(Protocol):
    """Protocol for recording one runtime connect-state event."""

    def record_connect_state(
        self, device_serial: str, timestamp: float, is_online: bool
    ) -> None:
        """Record one connect-state observation."""
        ...


class GroupReconciliationProtocol(Protocol):
    """Protocol for requesting one group reconciliation."""

    def schedule_group_reconciliation(
        self, device_name: str, timestamp: float
    ) -> None:
        """Request canonical group reconciliation from runtime root."""
        ...


class RefreshRequestProtocol(Protocol):
    """Protocol for requesting coordinator refresh."""

    async def __call__(self) -> None:
        """Request coordinator to refresh device states."""
        ...


class MqttConnectedProviderProtocol(Protocol):
    """Protocol for checking MQTT connection status."""

    def __call__(self) -> bool:
        """Check if MQTT is connected."""
        ...


class ReauthTriggerProtocol(Protocol):
    """Protocol for triggering re-authentication flow."""

    async def __call__(self, reason: str) -> None:
        """Trigger re-authentication flow."""
        ...


@dataclass(frozen=True, slots=True)
class RuntimeContext:
    """Unified dependency context for all runtime components.

    This context is constructed once during coordinator initialization and
    injected into all runtime components, eliminating the need for:
    - Lambda closures scattered across factory.py
    - Setter injection in MqttRuntime
    - Two-phase initialization patterns

    All ports are immutable references to formal coordinator-owned service objects or callbacks.
    """

    # Device resolution
    get_device_by_id: DeviceResolverProtocol

    # State management
    apply_properties_update: PropertyApplierProtocol
    schedule_listener_update: ListenerNotifierProtocol

    # Runtime signals
    record_connect_state: ConnectStateRecorderProtocol
    request_group_reconciliation: GroupReconciliationProtocol

    # Coordinator orchestration
    request_refresh: RefreshRequestProtocol
    trigger_reauth: ReauthTriggerProtocol

    # MQTT status
    is_mqtt_connected: MqttConnectedProviderProtocol

    def __post_init__(self) -> None:
        """Validate all dependencies are provided."""
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            if value is None:
                msg = f"RuntimeContext.{field_name} cannot be None"
                raise ValueError(msg)
