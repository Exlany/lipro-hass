"""Device snapshot building and reconciliation logic."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
import logging
from typing import TYPE_CHECKING, Any

from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.device.group_status import sync_mesh_group_extra_data

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

    async def _async_enrich_mesh_group_metadata(
        self,
        *,
        device_by_id: dict[str, LiproDevice],
        group_ids: list[str],
    ) -> None:
        """Enrich group devices with authoritative mesh topology metadata."""
        if not group_ids:
            return

        try:
            rows = await self._client.query_mesh_group_status(group_ids)
        except Exception as err:
            if isinstance(err, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
                raise
            _LOGGER.debug(
                "Mesh group metadata enrich failed (%s), keeping snapshot without topology",
                type(err).__name__,
            )
            return

        for row in rows:
            group_id = row.get("groupId") or row.get("id")
            if not isinstance(group_id, str) or not group_id.strip():
                continue
            device = device_by_id.get(group_id.strip())
            if device is None:
                continue
            sync_mesh_group_extra_data(device, row)

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

        while page <= max_pages:
            try:
                response = await self._client.get_device_list(page=page)
                devices_data = response.get("data") or response.get("devices", [])

                if not devices_data:
                    break

                all_devices.extend(devices_data)

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

        devices: dict[str, LiproDevice] = {}
        device_by_id: dict[str, LiproDevice] = {}
        identity_mapping: dict[str, LiproDevice] = {}
        iot_ids: list[str] = []
        group_ids: list[str] = []
        outlet_ids: list[str] = []
        cloud_serials: set[str] = set()
        diagnostic_gateway_devices: dict[str, LiproDevice] = {}

        for device_data in all_devices:
            try:
                if not self._device_filter.is_device_included(device_data):
                    _LOGGER.debug("Device filtered out by configuration")
                    continue

                device = LiproDevice.from_api_data(device_data)

                if device.is_gateway:
                    diagnostic_gateway_devices[device.serial] = device
                    continue

                devices[device.serial] = device

                identity_aliases = {device.serial}
                if device.iot_device_id:
                    identity_aliases.add(device.iot_device_id)
                for key in ("id", "iotId", "iotDeviceId", "groupId"):
                    candidate = device_data.get(key)
                    if isinstance(candidate, str) and candidate.strip():
                        identity_aliases.add(candidate.strip())

                device.extra_data["identity_aliases"] = sorted(identity_aliases)
                for identity_alias in identity_aliases:
                    device_by_id[identity_alias] = device
                    identity_mapping[identity_alias] = device

                cloud_serials.add(device.serial)

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

        await self._async_enrich_mesh_group_metadata(
            device_by_id=device_by_id,
            group_ids=group_ids,
        )

        self._device_identity_index.replace(identity_mapping)

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
