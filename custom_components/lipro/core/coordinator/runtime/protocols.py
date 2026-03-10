"""Runtime protocols for pure composition-based coordinator refactoring.

This module defines the contract layer for runtime components that will replace
inheritance-based mixins. Each protocol represents a focused runtime capability
that can be composed independently.

Design principles:
- Protocols are runtime-checkable for isinstance() validation
- All methods use strict type annotations
- Immutable state access via CoordinatorSharedState
- No side effects in property getters
- Async methods for I/O operations
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from ...device import LiproDevice


@runtime_checkable
class CommandRuntimeProtocol(Protocol):
    """Runtime protocol for device command dispatch and batch operations.

    This protocol defines the contract for sending commands to devices with
    optional confirmation tracking and batch execution support.
    """

    async def send_command(
        self,
        device_id: str,
        command: dict[str, Any],
        *,
        wait_confirmation: bool = True,
        timeout: float = 5.0,
    ) -> CommandResult:
        """Send a single command to a device.

        Args:
            device_id: Target device serial or identifier
            command: Command payload with action and properties
            wait_confirmation: Whether to wait for MQTT confirmation
            timeout: Maximum wait time for confirmation in seconds

        Returns:
            CommandResult with success status, trace, and optional error

        Raises:
            CommandTimeoutError: If confirmation wait exceeds timeout
            DeviceNotFoundError: If device_id does not exist
        """
        ...

    async def send_batch_commands(
        self,
        commands: list[tuple[str, dict[str, Any]]],
    ) -> list[CommandResult]:
        """Send multiple commands in parallel with best-effort semantics.

        Args:
            commands: List of (device_id, command) tuples

        Returns:
            List of CommandResult in the same order as input
            Failed commands return error results without raising exceptions
        """
        ...


@runtime_checkable
class DeviceRuntimeProtocol(Protocol):
    """Runtime protocol for device snapshot refresh operations.

    This protocol defines the contract for fetching and updating the device
    snapshot from the cloud API with incremental and force-refresh support.
    """

    async def refresh_devices(
        self,
        *,
        force: bool = False,
        incremental: bool = True,
    ) -> dict[str, LiproDevice]:
        """Refresh the device snapshot from cloud API.

        Args:
            force: Bypass cache and force full refresh
            incremental: Only fetch changed devices if supported

        Returns:
            Updated device map keyed by serial number

        Raises:
            LiproApiError: If API request fails
            LiproAuthError: If authentication is invalid
        """
        ...

    async def refresh_single_device(
        self,
        device_id: str,
    ) -> LiproDevice | None:
        """Refresh a single device by ID.

        Args:
            device_id: Device serial or identifier to refresh

        Returns:
            Updated LiproDevice or None if device no longer exists

        Raises:
            LiproApiError: If API request fails
        """
        ...


@runtime_checkable
class MqttRuntimeProtocol(Protocol):
    """Runtime protocol for MQTT connection lifecycle and message handling.

    This protocol defines the contract for managing MQTT client connection,
    subscription sync, and incoming message dispatch.
    """

    async def connect(self) -> bool:
        """Establish MQTT connection with broker.

        Returns:
            True if connection succeeded, False otherwise
            Does not raise exceptions on connection failure
        """
        ...

    async def disconnect(self) -> None:
        """Gracefully disconnect from MQTT broker.

        Ensures all pending messages are flushed and subscriptions are cleaned up.
        """
        ...

    async def handle_message(
        self,
        topic: str,
        payload: bytes,
    ) -> None:
        """Process incoming MQTT message.

        Args:
            topic: MQTT topic string
            payload: Raw message payload bytes

        Note:
            This method should not raise exceptions. Errors are logged internally.
        """
        ...

    @property
    def is_connected(self) -> bool:
        """Return current MQTT connection status.

        Returns:
            True if connected and ready to receive messages
        """
        ...


@runtime_checkable
class StateRuntimeProtocol(Protocol):
    """Runtime protocol for immutable device state access.

    This protocol defines the contract for reading device state without
    triggering side effects or mutations.
    """

    def get_device(self, device_id: str) -> LiproDevice | None:
        """Retrieve device by serial or identifier.

        Args:
            device_id: Device serial number or any known identifier

        Returns:
            LiproDevice if found, None otherwise
        """
        ...

    def get_all_devices(self) -> dict[str, LiproDevice]:
        """Retrieve all devices in current snapshot.

        Returns:
            Immutable view of device map keyed by serial number
        """
        ...

    def update_device_state(
        self,
        device_id: str,
        state: dict[str, Any],
    ) -> None:
        """Update device state from external source (e.g., MQTT push).

        Args:
            device_id: Target device serial
            state: Partial state update with property changes

        Note:
            This is the only mutation method in StateRuntimeProtocol.
            Updates are applied atomically and trigger entity callbacks.
        """
        ...


@runtime_checkable
class TuningRuntimeProtocol(Protocol):
    """Runtime protocol for adaptive tuning and performance optimization.

    This protocol defines the contract for adjusting polling intervals,
    confirmation timeouts, and other runtime parameters based on observed
    success rates and latency metrics.
    """

    def adjust_polling_interval(self, success_rate: float) -> None:
        """Adjust polling interval based on recent success rate.

        Args:
            success_rate: Success rate in range [0.0, 1.0]
                         Higher rates may allow longer intervals
        """
        ...

    def get_current_interval(self) -> float:
        """Get current adaptive polling interval.

        Returns:
            Current interval in seconds
        """
        ...


@runtime_checkable
class StatusRuntimeProtocol(Protocol):
    """Runtime protocol for device status polling operations.

    This protocol defines the contract for querying device online/offline
    status and property values via cloud API polling.
    """

    async def poll_device_status(
        self,
        device_id: str,
    ) -> dict[str, Any]:
        """Poll status for a single device.

        Args:
            device_id: Device serial to poll

        Returns:
            Status payload with online state and properties

        Raises:
            LiproApiError: If API request fails
            DeviceNotFoundError: If device does not exist
        """
        ...

    async def poll_all_status(self) -> dict[str, dict[str, Any]]:
        """Poll status for all devices in current snapshot.

        Returns:
            Map of device_id to status payload
            Failed polls return empty dict for that device

        Note:
            This method uses best-effort semantics and does not raise
            exceptions for individual device failures.
        """
        ...


# Type alias for command execution results
class CommandResult:
    """Result of a command execution with trace and error information."""

    success: bool
    trace: dict[str, Any]
    error: str | None

    def __init__(
        self,
        success: bool,
        trace: dict[str, Any],
        error: str | None = None,
    ) -> None:
        """Initialize command result.

        Args:
            success: Whether command succeeded
            trace: Execution trace with timing and route info
            error: Optional error message if failed
        """
        self.success = success
        self.trace = trace
        self.error = error


__all__ = [
    "CommandResult",
    "CommandRuntimeProtocol",
    "DeviceRuntimeProtocol",
    "MqttRuntimeProtocol",
    "StateRuntimeProtocol",
    "StatusRuntimeProtocol",
    "TuningRuntimeProtocol",
]
