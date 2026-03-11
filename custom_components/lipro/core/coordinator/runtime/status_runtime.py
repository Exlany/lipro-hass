"""Status runtime implementation with dependency injection."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .status import StatusExecutor, StatusScheduler, StatusStrategy

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from ...device import LiproDevice

_LOGGER = logging.getLogger(__name__)


class StatusRuntime:
    """Standalone status polling runtime with no coordinator dependency."""

    def __init__(
        self,
        *,
        power_query_interval: int,
        outlet_power_cycle_size: int,
        max_devices_per_query: int,
        initial_batch_size: int,
        query_device_status: Callable[
            [list[str]], Awaitable[dict[str, dict[str, Any]]]
        ],
        apply_properties_update: Callable[
            [LiproDevice, dict[str, Any], str], Awaitable[bool]
        ],
        get_device_by_id: Callable[[str], LiproDevice | None],
    ) -> None:
        """Initialize status runtime.

        Args:
            power_query_interval: Interval in seconds for power queries
            outlet_power_cycle_size: Number of outlets to query per cycle
            max_devices_per_query: Maximum devices per API query
            initial_batch_size: Initial batch size for state queries
            query_device_status: Async function to query device status
            apply_properties_update: Async function to apply property updates
            get_device_by_id: Function to look up devices
        """
        self._scheduler = StatusScheduler(
            power_query_interval=power_query_interval,
            outlet_power_cycle_size=outlet_power_cycle_size,
        )
        self._strategy = StatusStrategy(
            max_devices_per_query=max_devices_per_query,
            state_batch_size=initial_batch_size,
        )
        self._executor = StatusExecutor(
            query_device_status=query_device_status,
            apply_properties_update=apply_properties_update,
            get_device_by_id=get_device_by_id,
        )

    # Scheduler methods
    def should_query_power(self) -> bool:
        """Check if power query should run this cycle."""
        return self._scheduler.should_query_power()

    def mark_power_query_complete(self) -> None:
        """Mark power query as completed for this cycle."""
        self._scheduler.mark_power_query_complete()

    def get_outlet_power_query_slice(self, outlet_ids: list[str]) -> list[str]:
        """Get the next slice of outlets to query for power."""
        return self._scheduler.get_outlet_power_query_slice(outlet_ids)

    def advance_outlet_power_cycle(self, outlet_ids: list[str]) -> None:
        """Advance the outlet power query cycle offset."""
        self._scheduler.advance_outlet_power_cycle(outlet_ids)

    def reset_power_query_state(self) -> None:
        """Reset power query scheduling state."""
        self._scheduler.reset_power_query_state()

    # Strategy methods
    def compute_query_batches(self, device_ids: list[str]) -> list[list[str]]:
        """Split device IDs into query batches."""
        return self._strategy.compute_query_batches(device_ids)

    def should_query_device(
        self,
        device: LiproDevice,
        *,
        mqtt_connected: bool,
    ) -> bool:
        """Determine if a device should be queried via REST."""
        return self._strategy.should_query_device(device, mqtt_connected=mqtt_connected)

    def filter_query_candidates(
        self,
        devices: dict[str, LiproDevice],
        device_ids: list[str],
        *,
        mqtt_connected: bool,
    ) -> list[str]:
        """Filter device IDs to those needing REST queries."""
        return self._strategy.filter_query_candidates(
            devices,
            device_ids,
            mqtt_connected=mqtt_connected,
        )

    def get_current_batch_size(self) -> int:
        """Get current adaptive batch size."""
        return self._strategy.get_current_batch_size()

    def update_batch_size(self, new_size: int) -> None:
        """Update adaptive batch size."""
        self._strategy.update_batch_size(new_size)

    # Executor methods
    async def execute_status_query(self, device_ids: list[str]) -> dict[str, Any]:
        """Execute status query for a batch of devices."""
        return await self._executor.execute_status_query(device_ids)

    async def execute_parallel_queries(
        self,
        batches: list[list[str]],
        *,
        concurrency: int = 3,
    ) -> list[dict[str, Any]]:
        """Execute multiple status queries in parallel."""
        return await self._executor.execute_parallel_queries(
            batches, concurrency=concurrency
        )

    # Metrics
    def get_runtime_metrics(self) -> dict[str, Any]:
        """Get combined runtime metrics."""
        return {
            "scheduler": self._scheduler.get_scheduling_metrics(),
            "strategy": self._strategy.get_strategy_metrics(),
        }


__all__ = ["StatusRuntime"]
