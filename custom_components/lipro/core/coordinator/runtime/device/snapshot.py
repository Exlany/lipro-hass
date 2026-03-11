"""Device snapshot building and reconciliation logic."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
import logging
from typing import TYPE_CHECKING, Any

from custom_components.lipro.core.device import LiproDevice

if TYPE_CHECKING:
    from custom_components.lipro.core.api import LiproClient
    from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex

    from .filter import DeviceFilter

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class FetchedDeviceSnapshot:
    """Atomic container for refreshed device indexes."""

    devices: dict[str, LiproDevice]
    device_by_id: dict[str, LiproDevice]
    iot_ids: list[str]
    group_ids: list[str]
    outlet_ids: list[str]
    cloud_serials: set[str] = field(default_factory=set)
    diagnostic_gateway_devices: dict[str, LiproDevice] = field(default_factory=dict)


class SnapshotBuilder:
    """Builds device snapshots from API responses."""

    def __init__(
        self,
        *,
        client: LiproClient,
        device_identity_index: DeviceIdentityIndex,
        device_filter: DeviceFilter,
    ) -> None:
        """Initialize snapshot builder.

        Args:
            client: API client for device queries
            device_identity_index: Device identity index for alias registration
            device_filter: Device filter for inclusion checks
        """
        self._client = client
        self._device_identity_index = device_identity_index
        self._device_filter = device_filter

    async def build_full_snapshot(
        self,
        *,
        max_pages: int = 50,
    ) -> FetchedDeviceSnapshot:
        """Build complete device snapshot from paginated API.

        Args:
            max_pages: Maximum pagination pages to prevent infinite loops

        Returns:
            FetchedDeviceSnapshot with all devices and indexes
        """
        all_devices: list[dict[str, Any]] = []
        page = 1

        # Fetch all pages
        while page <= max_pages:
            try:
                response = await self._client.get_device_list(page=page)
                # Support both old format {"devices": [...]} and new format {"data": [...]}
                devices_data = response.get("data") or response.get("devices", [])

                if not devices_data:
                    break

                all_devices.extend(devices_data)

                # Check if more pages exist
                has_more = response.get("hasMore", False)
                if not has_more:
                    break

                page += 1
            except Exception as err:
                if isinstance(err, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
                    raise
                _LOGGER.error(
                    "Device list fetch failed on page %d (%s), stopping pagination",
                    page,
                    type(err).__name__,
                )
                break

        if page > max_pages:
            _LOGGER.error(
                "Device list pagination exceeded %d pages, aborting",
                max_pages,
            )

        # Build device objects and indexes
        devices: dict[str, LiproDevice] = {}
        device_by_id: dict[str, LiproDevice] = {}
        iot_ids: list[str] = []
        group_ids: list[str] = []
        outlet_ids: list[str] = []
        cloud_serials: set[str] = set()
        diagnostic_gateway_devices: dict[str, LiproDevice] = {}

        for device_data in all_devices:
            try:
                # Apply filter before parsing
                if not self._device_filter.is_device_included(device_data):
                    _LOGGER.debug(
                        "Device filtered out by configuration",
                    )
                    continue

                device = LiproDevice.from_api_data(device_data)

                # Skip gateway devices (track for diagnostics only)
                if device.is_gateway:
                    diagnostic_gateway_devices[device.serial] = device
                    continue

                # Register identity aliases
                self._device_identity_index.register(device.serial, device)
                if device.iot_device_id:
                    self._device_identity_index.register(device.iot_device_id, device)

                # Add to indexes
                devices[device.serial] = device
                if device.iot_device_id:
                    device_by_id[device.iot_device_id] = device

                cloud_serials.add(device.serial)

                # Categorize by type
                if device.is_group:
                    if device.iot_device_id:
                        group_ids.append(device.iot_device_id)
                elif device.is_outlet:
                    if device.iot_device_id:
                        outlet_ids.append(device.iot_device_id)
                elif device.iot_device_id:
                    iot_ids.append(device.iot_device_id)

            except Exception as err:
                if isinstance(err, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
                    raise
                _LOGGER.debug(
                    "Failed to parse device from API data (%s: %s), skipping",
                    type(err).__name__,
                    str(err),
                )

        _LOGGER.info(
            "Built device snapshot: %d devices (%d IoT, %d groups, %d outlets)",
            len(devices),
            len(iot_ids),
            len(group_ids),
            len(outlet_ids),
        )

        return FetchedDeviceSnapshot(
            devices=devices,
            device_by_id=device_by_id,
            iot_ids=iot_ids,
            group_ids=group_ids,
            outlet_ids=outlet_ids,
            cloud_serials=cloud_serials,
            diagnostic_gateway_devices=diagnostic_gateway_devices,
        )


__all__ = [
    "FetchedDeviceSnapshot",
    "SnapshotBuilder",
]
