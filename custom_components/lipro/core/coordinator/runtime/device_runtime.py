"""Standalone device runtime with dependency injection."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import TYPE_CHECKING

from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)

from ..types import PropertyValue
from .device.filter import DeviceFilter, parse_filter_config
from .device.refresh_strategy import RefreshStrategy, StaleDeviceTracker
from .device.snapshot import (
    FetchedDeviceSnapshot,
    RuntimeSnapshotRefreshFailure,
    RuntimeSnapshotRefreshRejectedError,
    SnapshotBuilder,
)

if TYPE_CHECKING:
    from custom_components.lipro.core.auth import LiproAuthManager
    from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex
    from custom_components.lipro.core.protocol import LiproProtocolFacade

_LOGGER = logging.getLogger(__name__)


class DeviceRuntime:
    """Standalone device runtime with dependency injection.

    This component manages full device snapshot refresh and stale device
    reconciliation without inheriting from coordinator base.
    """

    def __init__(
        self,
        *,
        protocol: LiproProtocolFacade,
        auth_manager: LiproAuthManager,
        device_identity_index: DeviceIdentityIndex,
        filter_config_options: Mapping[str, PropertyValue] | None = None,
    ) -> None:
        """Initialize device runtime.

        Args:
            protocol: Formal protocol facade for device queries
            auth_manager: Auth manager for credential validation
            device_identity_index: Device identity index for alias registration
            filter_config_options: Optional filter configuration from config entry
        """
        self._protocol = protocol
        self._auth_manager = auth_manager
        self._device_identity_index = device_identity_index

        filter_config = parse_filter_config(filter_config_options or {})
        self._device_filter = DeviceFilter(config=filter_config)

        self._refresh_strategy = RefreshStrategy()
        self._stale_tracker = StaleDeviceTracker()
        self._snapshot_builder = SnapshotBuilder(
            client=protocol,
            device_identity_index=device_identity_index,
            device_filter=self._device_filter,
        )

        self._last_snapshot: FetchedDeviceSnapshot | None = None
        self._last_refresh_failure: RuntimeSnapshotRefreshFailure | None = None
        self._cloud_serials_last_seen: set[str] = set()

    @staticmethod
    def _classify_refresh_failure(
        err: Exception,
        *,
        kept_last_known_good: bool,
    ) -> RuntimeSnapshotRefreshFailure:
        """Normalize a non-runtime exception into the runtime failure view."""
        if isinstance(err, (LiproRefreshTokenExpiredError, LiproAuthError)):
            stage = "auth"
        elif isinstance(err, (LiproConnectionError, LiproApiError)):
            stage = "protocol"
        else:
            stage = "runtime"
        return RuntimeSnapshotRefreshFailure(
            stage=stage,
            error_type=type(err).__name__,
            kept_last_known_good=kept_last_known_good,
        )

    async def _async_build_snapshot(
        self,
        *,
        retained_last_known_good: bool,
    ) -> FetchedDeviceSnapshot:
        """Build one full snapshot and normalize retained failure state."""
        try:
            snapshot = await self._snapshot_builder.build_full_snapshot()
        except RuntimeSnapshotRefreshRejectedError as err:
            runtime_err = (
                err.with_retained_last_known_good()
                if retained_last_known_good and not err.kept_last_known_good
                else err
            )
            self._last_refresh_failure = runtime_err.failure
            if retained_last_known_good:
                _LOGGER.warning(
                    "Device refresh rejected (%s), retaining last-known-good snapshot",
                    runtime_err.stage,
                )
            if runtime_err is err:
                raise
            raise runtime_err from err
        except (
            LiproRefreshTokenExpiredError,
            LiproAuthError,
            LiproConnectionError,
            LiproApiError,
            RuntimeError,
            ValueError,
            TypeError,
            LookupError,
        ) as err:
            self._last_refresh_failure = self._classify_refresh_failure(
                err,
                kept_last_known_good=retained_last_known_good,
            )
            if retained_last_known_good:
                _LOGGER.warning(
                    "Device refresh failed (%s), retaining last-known-good snapshot",
                    type(err).__name__,
                )
            raise

        self._refresh_strategy.mark_refreshed()
        self._last_snapshot = snapshot
        self._last_refresh_failure = None
        return snapshot

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

        if self._refresh_strategy.should_refresh():
            snapshot = await self._async_build_snapshot(
                retained_last_known_good=self._last_snapshot is not None,
            )
            _LOGGER.info(
                "Full device refresh completed: %d devices",
                len(snapshot.devices),
            )
            return snapshot

        if self._last_snapshot is None:
            return await self._async_build_snapshot(retained_last_known_good=False)

        _LOGGER.debug("Device list refresh skipped; reusing cached snapshot")
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

        self._cloud_serials_last_seen = current_snapshot.cloud_serials.copy()

        return missing_cycles, removable

    def request_force_refresh(self) -> None:
        """Request immediate full refresh on next call."""
        self._refresh_strategy.request_force_refresh()

    def get_last_snapshot(self) -> FetchedDeviceSnapshot | None:
        """Get last fetched device snapshot."""
        return self._last_snapshot

    def get_last_refresh_failure(self) -> RuntimeSnapshotRefreshFailure | None:
        """Return the last structured refresh failure, if any."""
        return self._last_refresh_failure

    def should_refresh_device_list(self) -> bool:
        """Check if device list should be refreshed.

        Returns:
            True if refresh is needed
        """
        return self._refresh_strategy.should_refresh()

    def reset(self) -> None:
        """Reset runtime state (for testing or coordinator restart)."""
        self._refresh_strategy.reset()
        self._stale_tracker.reset()
        self._last_snapshot = None
        self._last_refresh_failure = None
        self._cloud_serials_last_seen.clear()


__all__ = ["DeviceRuntime"]
