"""Device runtime implementation for coordinator refactoring."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .device.batch_optimizer import DeviceBatchOptimizer
from .device.filter import DeviceFilter, parse_filter_config
from .device.incremental import IncrementalRefreshStrategy
from .device.refresh_strategy import RefreshStrategy, StaleDeviceTracker
from .device.snapshot import FetchedDeviceSnapshot, SnapshotBuilder

if TYPE_CHECKING:
    from ...api import LiproClient
    from ...auth import LiproAuthManager
    from ...device.identity_index import DeviceIdentityIndex

_LOGGER = logging.getLogger(__name__)


class DeviceRuntime:
    """Standalone device runtime with dependency injection.

    This component manages device snapshot refresh, incremental updates,
    and stale device reconciliation without inheriting from coordinator base.
    """

    def __init__(
        self,
        *,
        client: LiproClient,
        auth_manager: LiproAuthManager,
        device_identity_index: DeviceIdentityIndex,
        filter_config_options: dict[str, Any] | None = None,
    ) -> None:
        """Initialize device runtime.

        Args:
            client: API client for device queries
            auth_manager: Auth manager for credential validation
            device_identity_index: Device identity index for alias registration
            filter_config_options: Optional filter configuration from config entry
        """
        self._client = client
        self._auth_manager = auth_manager
        self._device_identity_index = device_identity_index

        # Parse filter configuration
        filter_config = parse_filter_config(filter_config_options or {})
        self._device_filter = DeviceFilter(config=filter_config)

        # Initialize sub-components
        self._refresh_strategy = RefreshStrategy()
        self._stale_tracker = StaleDeviceTracker()
        self._batch_optimizer = DeviceBatchOptimizer()
        self._snapshot_builder = SnapshotBuilder(
            client=client,
            device_identity_index=device_identity_index,
            device_filter=self._device_filter,
        )
        self._incremental_strategy = IncrementalRefreshStrategy(client=client)

        # Runtime state
        self._last_snapshot: FetchedDeviceSnapshot | None = None
        self._cloud_serials_last_seen: set[str] = set()

    async def refresh_devices(
        self,
        *,
        force: bool = False,
    ) -> FetchedDeviceSnapshot:
        """Refresh device snapshot from cloud API.

        Args:
            force: Force full refresh regardless of timing

        Returns:
            FetchedDeviceSnapshot with updated device data

        Raises:
            LiproApiError: If API request fails
        """
        if force:
            self._refresh_strategy.request_force_refresh()

        # Check if full refresh is needed
        if self._refresh_strategy.should_refresh():
            snapshot = await self._snapshot_builder.build_full_snapshot()
            self._refresh_strategy.mark_refreshed()
            self._last_snapshot = snapshot

            _LOGGER.info(
                "Full device refresh completed: %d devices",
                len(snapshot.devices),
            )
            return snapshot

        # Incremental refresh using existing snapshot
        if self._last_snapshot is None:
            # First refresh must be full
            snapshot = await self._snapshot_builder.build_full_snapshot()
            self._refresh_strategy.mark_refreshed()
            self._last_snapshot = snapshot
            return snapshot

        # Perform incremental state update
        await self._incremental_strategy.refresh_device_states(
            iot_ids=self._last_snapshot.iot_ids,
            group_ids=self._last_snapshot.group_ids,
            outlet_ids=self._last_snapshot.outlet_ids,
            devices=self._last_snapshot.devices,
            batch_optimizer=self._batch_optimizer,
        )

        _LOGGER.debug("Incremental device refresh completed")
        return self._last_snapshot

    def compute_stale_devices(
        self,
        *,
        current_snapshot: FetchedDeviceSnapshot,
    ) -> tuple[dict[str, int], set[str]]:
        """Compute stale device reconciliation plan.

        Args:
            current_snapshot: Latest device snapshot

        Returns:
            Tuple of (missing_cycles, removable_serials)
        """
        missing_cycles, removable = self._stale_tracker.update(
            previous_serials=self._cloud_serials_last_seen,
            current_serials=current_snapshot.cloud_serials,
        )

        # Update last seen serials for next comparison
        self._cloud_serials_last_seen = current_snapshot.cloud_serials.copy()

        return missing_cycles, removable

    def request_force_refresh(self) -> None:
        """Request immediate full refresh on next call."""
        self._refresh_strategy.request_force_refresh()

    def get_last_snapshot(self) -> FetchedDeviceSnapshot | None:
        """Get last fetched device snapshot."""
        return self._last_snapshot

    def reset(self) -> None:
        """Reset runtime state (for testing or coordinator restart)."""
        self._refresh_strategy.reset()
        self._stale_tracker.reset()
        self._last_snapshot = None
        self._cloud_serials_last_seen.clear()


__all__ = ["DeviceRuntime"]
