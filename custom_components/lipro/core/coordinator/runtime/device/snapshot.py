"""Device snapshot building and reconciliation logic."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Protocol, cast

from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.device.group_status import sync_mesh_group_extra_data
from custom_components.lipro.core.protocol.contracts import (
    CanonicalDeviceListItem,
    CanonicalDeviceListPage,
    CanonicalMeshGroupStatusRow,
)

from .snapshot_models import (
    FetchedDeviceSnapshot,
    RuntimeSnapshotRefreshFailure,
    RuntimeSnapshotRefreshRejectedError,
)
from .snapshot_support import (
    DeviceRow,
    SnapshotAssembly,
    canonical_page_has_more,
    canonicalize_device_row,
    device_ref_from_row,
    record_snapshot_device,
)

if TYPE_CHECKING:
    from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex

    from .filter import DeviceFilter

_LOGGER = logging.getLogger(__name__)
_DEFAULT_DEVICE_PAGE_SIZE = 100

class SnapshotProtocolPort(Protocol):
    """Minimal protocol-facade surface consumed by snapshot builder."""

    async def get_devices(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> CanonicalDeviceListPage:
        """Return one canonical device-list page."""

    async def query_mesh_group_status(
        self,
        group_ids: list[str],
    ) -> list[CanonicalMeshGroupStatusRow]:
        """Return canonical mesh-group rows for the requested groups."""

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
            normalized_rows = await self._protocol.query_mesh_group_status(group_ids)
        except asyncio.CancelledError:
            raise
        except (
            LiproRefreshTokenExpiredError,
            LiproAuthError,
            LiproConnectionError,
            LiproApiError,
            RuntimeSnapshotRefreshRejectedError,
        ):
            raise
        except (RuntimeError, ValueError, TypeError, LookupError) as err:
            raise RuntimeSnapshotRefreshRejectedError(
                stage="mesh_group_topology",
                cause_type=type(err).__name__,
            ) from err

        for row in normalized_rows:
            group_id = row.get("groupId")
            if not isinstance(group_id, str) or not group_id.strip():
                continue
            device = device_by_id.get(group_id.strip())
            if device is None:
                continue
            sync_mesh_group_extra_data(device, cast(dict[str, Any], row))

    async def _fetch_device_page(self, *, page: int) -> tuple[list[DeviceRow], bool]:
        """Fetch one device page through the formal canonical contract."""
        offset = (page - 1) * _DEFAULT_DEVICE_PAGE_SIZE
        response = await self._protocol.get_devices(
            offset=offset,
            limit=_DEFAULT_DEVICE_PAGE_SIZE,
        )
        devices_payload = response.get("devices", [])
        if not isinstance(devices_payload, list):
            raise RuntimeSnapshotRefreshRejectedError(
                stage="page_payload",
                page=page,
                cause_type=type(devices_payload).__name__,
            )

        raw_devices: list[CanonicalDeviceListItem] = []
        for row in devices_payload:
            if not isinstance(row, dict):
                raise RuntimeSnapshotRefreshRejectedError(
                    stage="page_row",
                    page=page,
                    cause_type=type(row).__name__,
                )
            raw_devices.append(row)

        devices_data = cast(list[DeviceRow], [dict(row) for row in raw_devices])
        return devices_data, canonical_page_has_more(
            offset=offset,
            devices_data=raw_devices,
            total=response.get("total"),
        )

    def __init__(
        self,
        *,
        protocol: SnapshotProtocolPort,
        device_identity_index: DeviceIdentityIndex,
        device_filter: DeviceFilter,
    ) -> None:
        """Initialize snapshot builder."""
        self._protocol = protocol
        self._device_identity_index = device_identity_index
        self._device_filter = device_filter

    async def _collect_snapshot_pages(
        self,
        *,
        max_pages: int,
    ) -> list[tuple[int, DeviceRow]]:
        """Collect paginated device rows while preserving page provenance."""
        all_devices: list[tuple[int, DeviceRow]] = []
        page = 1
        has_more = False

        while page <= max_pages:
            try:
                devices_data, has_more = await self._fetch_device_page(page=page)
            except asyncio.CancelledError:
                raise
            except (
                LiproRefreshTokenExpiredError,
                LiproAuthError,
                LiproConnectionError,
                LiproApiError,
                RuntimeSnapshotRefreshRejectedError,
            ):
                raise
            except (RuntimeError, ValueError, TypeError, LookupError) as err:
                raise RuntimeSnapshotRefreshRejectedError(
                    stage="fetch_page",
                    page=page,
                    cause_type=type(err).__name__,
                ) from err

            if not devices_data:
                break

            all_devices.extend((page, row) for row in devices_data)
            if not has_more:
                break
            page += 1

        if page > max_pages and has_more:
            raise RuntimeSnapshotRefreshRejectedError(
                stage="pagination_limit",
                page=max_pages,
                cause_type="max_pages",
            )
        return all_devices

    def _record_snapshot_row(
        self,
        *,
        page_number: int,
        device_data: DeviceRow,
        assembly: SnapshotAssembly,
    ) -> None:
        """Normalize, filter, parse, and record one snapshot row."""
        try:
            normalized_row = canonicalize_device_row(device_data)
            if not self._device_filter.is_device_included(normalized_row):
                _LOGGER.debug("Device filtered out by configuration")
                return

            device = LiproDevice.from_api_data(cast(dict[str, object], normalized_row))
        except asyncio.CancelledError:
            raise
        except (RuntimeError, ValueError, TypeError, LookupError) as err:
            raise RuntimeSnapshotRefreshRejectedError(
                stage="parse_device",
                page=page_number,
                device_ref=device_ref_from_row(device_data),
                cause_type=type(err).__name__,
            ) from err

        record_snapshot_device(
            normalized_row=normalized_row,
            device=device,
            assembly=assembly,
        )

    def _build_snapshot_assembly(
        self,
        *,
        all_devices: list[tuple[int, DeviceRow]],
    ) -> SnapshotAssembly:
        """Build the in-memory snapshot assembly from canonical rows."""
        assembly = SnapshotAssembly()
        for page_number, device_data in all_devices:
            self._record_snapshot_row(
                page_number=page_number,
                device_data=device_data,
                assembly=assembly,
            )
        return assembly

    def _log_snapshot_summary(self, assembly: SnapshotAssembly) -> None:
        """Log the final snapshot summary after successful assembly."""
        _LOGGER.info(
            "Built device snapshot: %d devices (%d IoT, %d groups, %d outlets)",
            len(assembly.devices),
            len(assembly.iot_ids),
            len(assembly.group_ids),
            len(assembly.outlet_ids),
        )

    def _build_fetched_snapshot(self, assembly: SnapshotAssembly) -> FetchedDeviceSnapshot:
        """Freeze assembly data into the fetched snapshot value object."""
        return FetchedDeviceSnapshot(
            devices=assembly.devices,
            device_by_id=assembly.device_by_id,
            iot_ids=assembly.iot_ids,
            group_ids=assembly.group_ids,
            outlet_ids=assembly.outlet_ids,
            identity_aliases_by_serial=assembly.identity_aliases_by_serial,
            cloud_serials=assembly.cloud_serials,
            diagnostic_gateway_devices=assembly.diagnostic_gateway_devices,
        )

    async def build_full_snapshot(
        self,
        *,
        max_pages: int = 50,
    ) -> FetchedDeviceSnapshot:
        """Build complete device snapshot from paginated API."""
        all_devices = await self._collect_snapshot_pages(max_pages=max_pages)
        assembly = self._build_snapshot_assembly(all_devices=all_devices)

        await self._async_enrich_mesh_group_metadata(
            device_by_id=assembly.device_by_id,
            group_ids=assembly.group_ids,
        )
        self._device_identity_index.replace(assembly.identity_mapping)
        self._log_snapshot_summary(assembly)
        return self._build_fetched_snapshot(assembly)


__all__ = [
    "FetchedDeviceSnapshot",
    "RuntimeSnapshotRefreshFailure",
    "RuntimeSnapshotRefreshRejectedError",
    "SnapshotBuilder",
]
