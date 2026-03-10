"""Status polling scheduler for coordinating device status queries."""

from __future__ import annotations

import logging
from time import monotonic
from typing import Any

_LOGGER = logging.getLogger(__name__)


class StatusScheduler:
    """Schedule and coordinate device status polling operations."""

    def __init__(
        self,
        *,
        power_query_interval: int,
        outlet_power_cycle_size: int,
    ) -> None:
        """Initialize status scheduler.

        Args:
            power_query_interval: Interval in seconds for power queries
            outlet_power_cycle_size: Number of outlets to query per cycle
        """
        self._power_query_interval = power_query_interval
        self._outlet_power_cycle_size = outlet_power_cycle_size
        self._last_power_query_at: float = 0.0
        self._outlet_power_cycle_offset: int = 0

    def should_query_power(self) -> bool:
        """Check if power query should run this cycle.

        Returns:
            True if power query interval has elapsed
        """
        now = monotonic()
        elapsed = now - self._last_power_query_at
        return elapsed >= self._power_query_interval

    def mark_power_query_complete(self) -> None:
        """Mark power query as completed for this cycle."""
        self._last_power_query_at = monotonic()

    def get_outlet_power_query_slice(
        self,
        outlet_ids: list[str],
    ) -> list[str]:
        """Get the next slice of outlets to query for power.

        Args:
            outlet_ids: Full list of outlet device IDs

        Returns:
            Slice of outlet IDs for this cycle
        """
        if not outlet_ids:
            return []

        total = len(outlet_ids)
        if total <= self._outlet_power_cycle_size:
            return outlet_ids

        start = self._outlet_power_cycle_offset
        end = start + self._outlet_power_cycle_size

        if end <= total:
            slice_ids = outlet_ids[start:end]
        else:
            # Wrap around to beginning
            slice_ids = outlet_ids[start:] + outlet_ids[: end - total]

        return slice_ids

    def advance_outlet_power_cycle(self, outlet_ids: list[str]) -> None:
        """Advance the outlet power query cycle offset.

        Args:
            outlet_ids: Full list of outlet device IDs
        """
        if not outlet_ids:
            self._outlet_power_cycle_offset = 0
            return

        total = len(outlet_ids)
        self._outlet_power_cycle_offset = (
            self._outlet_power_cycle_offset + self._outlet_power_cycle_size
        ) % total

    def reset_power_query_state(self) -> None:
        """Reset power query scheduling state."""
        self._last_power_query_at = 0.0
        self._outlet_power_cycle_offset = 0

    def get_scheduling_metrics(self) -> dict[str, Any]:
        """Get current scheduling metrics.

        Returns:
            Dictionary with scheduling state
        """
        now = monotonic()
        return {
            "power_query_interval": self._power_query_interval,
            "last_power_query_elapsed": (
                now - self._last_power_query_at if self._last_power_query_at else None
            ),
            "outlet_cycle_offset": self._outlet_power_cycle_offset,
            "outlet_cycle_size": self._outlet_power_cycle_size,
        }


__all__ = ["StatusScheduler"]
