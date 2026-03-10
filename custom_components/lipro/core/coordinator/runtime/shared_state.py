"""Immutable shared state for coordinator runtime components.

This module provides a frozen dataclass that encapsulates all shared state
accessed by runtime components. Using immutable state enables:

- Thread-safe reads without locks
- Clear state transitions via copy-on-write
- Easier testing with predictable snapshots
- No hidden mutations or side effects

Design principles:
- All fields are immutable (frozen=True)
- State updates create new instances via replace()
- No mutable collections in public API
- Timestamps use monotonic time for consistency
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...device import LiproDevice


@dataclass(frozen=True)
class CoordinatorSharedState:
    """Immutable shared state snapshot for runtime components.

    This class represents a point-in-time snapshot of coordinator state that
    can be safely shared across runtime components without synchronization.

    Attributes:
        devices: Device map keyed by serial number
        mqtt_connected: Current MQTT connection status
        biz_id: Business ID for MQTT topic construction
        last_refresh_at: Monotonic timestamp of last device refresh
        polling_interval: Current adaptive polling interval in seconds
        command_confirmation_timeout: Timeout for command confirmations
        debug_mode: Whether debug tracing is enabled
    """

    devices: dict[str, LiproDevice] = field(default_factory=dict)
    mqtt_connected: bool = False
    biz_id: str | None = None
    last_refresh_at: float = 0.0
    polling_interval: float = 30.0
    command_confirmation_timeout: float = 5.0
    debug_mode: bool = False

    def with_devices(
        self,
        devices: dict[str, LiproDevice],
    ) -> CoordinatorSharedState:
        """Create new state with updated device snapshot.

        Args:
            devices: New device map to replace current snapshot

        Returns:
            New CoordinatorSharedState instance with updated devices
        """
        return replace(self, devices=devices)

    def with_mqtt_connected(
        self,
        connected: bool,
    ) -> CoordinatorSharedState:
        """Create new state with updated MQTT connection status.

        Args:
            connected: New MQTT connection status

        Returns:
            New CoordinatorSharedState instance with updated status
        """
        return replace(self, mqtt_connected=connected)

    def with_biz_id(
        self,
        biz_id: str | None,
    ) -> CoordinatorSharedState:
        """Create new state with updated business ID.

        Args:
            biz_id: New business ID for MQTT topics

        Returns:
            New CoordinatorSharedState instance with updated biz_id
        """
        return replace(self, biz_id=biz_id)

    def with_last_refresh_at(
        self,
        timestamp: float,
    ) -> CoordinatorSharedState:
        """Create new state with updated refresh timestamp.

        Args:
            timestamp: Monotonic timestamp of refresh completion

        Returns:
            New CoordinatorSharedState instance with updated timestamp
        """
        return replace(self, last_refresh_at=timestamp)

    def with_polling_interval(
        self,
        interval: float,
    ) -> CoordinatorSharedState:
        """Create new state with updated polling interval.

        Args:
            interval: New polling interval in seconds

        Returns:
            New CoordinatorSharedState instance with updated interval
        """
        return replace(self, polling_interval=interval)

    def with_command_confirmation_timeout(
        self,
        timeout: float,
    ) -> CoordinatorSharedState:
        """Create new state with updated command confirmation timeout.

        Args:
            timeout: New timeout in seconds

        Returns:
            New CoordinatorSharedState instance with updated timeout
        """
        return replace(self, command_confirmation_timeout=timeout)

    def with_debug_mode(
        self,
        enabled: bool,
    ) -> CoordinatorSharedState:
        """Create new state with updated debug mode.

        Args:
            enabled: Whether debug tracing should be enabled

        Returns:
            New CoordinatorSharedState instance with updated debug mode
        """
        return replace(self, debug_mode=enabled)

    def get_device(self, device_id: str) -> LiproDevice | None:
        """Retrieve device by serial number.

        Args:
            device_id: Device serial to lookup

        Returns:
            LiproDevice if found, None otherwise
        """
        return self.devices.get(device_id)

    def get_all_devices(self) -> dict[str, LiproDevice]:
        """Retrieve all devices in current snapshot.

        Returns:
            Immutable view of device map

        Note:
            The returned dict is the internal reference. Callers must not
            mutate it. Consider this a read-only view.

        Deprecated:
            Use StateRuntime.get_all_devices() for consistent state access.
            This method delegates to the same underlying data source.
        """
        return self.devices

    @property
    def device_count(self) -> int:
        """Return total number of devices in snapshot."""
        return len(self.devices)

    @property
    def has_devices(self) -> bool:
        """Return whether any devices exist in snapshot."""
        return bool(self.devices)

    def to_diagnostic_dict(self) -> dict[str, Any]:
        """Export state as diagnostic dictionary.

        Returns:
            Dictionary with state summary for diagnostics
        """
        return {
            "device_count": self.device_count,
            "mqtt_connected": self.mqtt_connected,
            "biz_id": self.biz_id,
            "last_refresh_at": self.last_refresh_at,
            "polling_interval": self.polling_interval,
            "command_confirmation_timeout": self.command_confirmation_timeout,
            "debug_mode": self.debug_mode,
        }


__all__ = [
    "CoordinatorSharedState",
]
