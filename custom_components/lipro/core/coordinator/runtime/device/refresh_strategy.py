"""Device refresh strategy and timing logic."""

from __future__ import annotations

import logging
from time import monotonic
from typing import Final

_LOGGER = logging.getLogger(__name__)

# Periodic full device-list refresh to discover newly paired devices.
DEVICE_LIST_REFRESH_INTERVAL_SECONDS: Final[int] = 600

# Number of consecutive full-device-list fetches a device can be missing
# before being removed from HA device registry.
STALE_DEVICE_REMOVE_THRESHOLD: Final[int] = 3


class RefreshStrategy:
    """Manages device refresh timing and force-refresh decisions."""

    def __init__(
        self,
        *,
        refresh_interval: int = DEVICE_LIST_REFRESH_INTERVAL_SECONDS,
    ) -> None:
        """Initialize refresh strategy.

        Args:
            refresh_interval: Seconds between periodic full refreshes
        """
        self._refresh_interval = refresh_interval
        self._last_refresh_at: float = 0.0
        self._force_refresh: bool = False

    def should_refresh(self) -> bool:
        """Check if a full device list refresh is needed.

        Returns:
            True if refresh interval elapsed or force flag set
        """
        if self._force_refresh:
            return True

        now = monotonic()
        elapsed = now - self._last_refresh_at
        return elapsed >= self._refresh_interval

    def mark_refreshed(self) -> None:
        """Record successful refresh completion."""
        self._last_refresh_at = monotonic()
        self._force_refresh = False

    def request_force_refresh(self) -> None:
        """Request immediate refresh on next check."""
        self._force_refresh = True
        _LOGGER.debug("Force device refresh requested")

    def reset(self) -> None:
        """Reset refresh state (for testing or coordinator restart)."""
        self._last_refresh_at = 0.0
        self._force_refresh = False


class StaleDeviceTracker:
    """Tracks missing devices across refresh cycles."""

    def __init__(self, *, remove_threshold: int = STALE_DEVICE_REMOVE_THRESHOLD) -> None:
        """Initialize stale device tracker.

        Args:
            remove_threshold: Cycles before device removal
        """
        self._remove_threshold = remove_threshold
        self._missing_cycles: dict[str, int] = {}

    def update(
        self,
        *,
        previous_serials: set[str],
        current_serials: set[str],
    ) -> tuple[dict[str, int], set[str]]:
        """Update missing cycle counters and compute removable devices.

        Args:
            previous_serials: Serials from last refresh
            current_serials: Serials from current refresh

        Returns:
            Tuple of (updated_missing_cycles, removable_serials)
        """
        # Preserve counters for devices still missing
        updated_cycles = {
            serial: count
            for serial, count in self._missing_cycles.items()
            if serial not in current_serials
        }

        # Identify stale devices (previously seen but now missing)
        stale_serials = (previous_serials | set(updated_cycles)) - current_serials

        removable: set[str] = set()
        for serial in stale_serials:
            miss_count = updated_cycles.get(serial, 0) + 1
            updated_cycles[serial] = miss_count
            if miss_count >= self._remove_threshold:
                removable.add(serial)

        self._missing_cycles = updated_cycles
        return updated_cycles, removable

    def get_missing_cycles(self) -> dict[str, int]:
        """Get current missing cycle counters."""
        return self._missing_cycles.copy()

    def reset(self) -> None:
        """Clear all missing cycle counters."""
        self._missing_cycles.clear()


__all__ = [
    "DEVICE_LIST_REFRESH_INTERVAL_SECONDS",
    "STALE_DEVICE_REMOVE_THRESHOLD",
    "RefreshStrategy",
    "StaleDeviceTracker",
]
