"""Device snapshot building and reconciliation logic."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
import inspect
import logging
from typing import TYPE_CHECKING, Any, Protocol, cast

from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from custom_components.lipro.core.api.types import DeviceListItem, DeviceListResponse
from custom_components.lipro.core.coordinator.types import PropertyDict
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.device.group_status import sync_mesh_group_extra_data
from custom_components.lipro.core.protocol.contracts import CanonicalMeshGroupStatusRow

from .snapshot_models import (
    FetchedDeviceSnapshot,
    RuntimeSnapshotRefreshFailure,
    RuntimeSnapshotRefreshRejectedError,
)

if TYPE_CHECKING:
    from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex

    from .filter import DeviceFilter

_LOGGER = logging.getLogger(__name__)
_DEFAULT_DEVICE_PAGE_SIZE = 100

type DeviceRow = PropertyDict

class SnapshotProtocolClient(Protocol):
    """Minimal protocol-facade surface consumed by snapshot builder."""

    async def get_devices(self, offset: int = 0, limit: int = 100) -> DeviceListResponse:
        """Return one canonical device-list page."""

    async def query_mesh_group_status(
        self,
        group_ids: list[str],
    ) -> list[CanonicalMeshGroupStatusRow]:
        """Return raw/canonical mesh-group rows for the requested groups."""

    @property
    def contracts(self) -> SnapshotProtocolContracts:
        """Expose protocol-owned normalization helpers."""


class SnapshotProtocolContracts(Protocol):
    """Contract helpers required by runtime snapshot builder."""

    def normalize_mesh_group_status_rows(
        self,
        payload: object,
    ) -> list[CanonicalMeshGroupStatusRow]:
        """Normalize mesh-group topology rows."""


class SnapshotBuilder:
    """Builds device snapshots from API responses."""

    @staticmethod
    def _canonicalize_device_row(device_data: Mapping[str, object]) -> DeviceRow:
        """Return one runtime-ready canonical device row."""
        normalized = dict(device_data)
        identity_aliases = normalized.get("identityAliases")
        if not isinstance(identity_aliases, list):
            derived_aliases = {
                candidate.strip()
                for candidate in (
                    normalized.get("serial"),
                    normalized.get("iotDeviceId"),
                )
                if isinstance(candidate, str) and candidate.strip()
            }
            if derived_aliases:
                normalized["identityAliases"] = sorted(derived_aliases)
        return cast(DeviceRow, normalized)

    @staticmethod
    def _device_ref_from_row(device_data: Mapping[str, object]) -> str | None:
        """Return the best-effort device reference for one row."""
        for key in ("serial", "iotDeviceId", "deviceId"):
            candidate = device_data.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        return None

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
            normalized_rows_obj: object = self._contracts.normalize_mesh_group_status_rows(
                rows
            )
            if inspect.isawaitable(normalized_rows_obj):
                normalized_rows_obj = await normalized_rows_obj
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

        if isinstance(normalized_rows_obj, list):
            normalized_rows = normalized_rows_obj
        else:
            normalized_rows = [row for row in rows if isinstance(row, dict)]

        for row in normalized_rows:
            group_id = row.get("groupId")
            if not isinstance(group_id, str) or not group_id.strip():
                continue
            device = device_by_id.get(group_id.strip())
            if device is None:
                continue
            sync_mesh_group_extra_data(device, cast(dict[str, Any], row))

    @staticmethod
    def _canonical_page_has_more(
        *,
        offset: int,
        devices_data: list[DeviceListItem],
        total: object,
    ) -> bool:
        """Return whether one canonical device page has more rows to fetch."""
        if isinstance(total, bool):
            total_count = offset + len(devices_data)
        elif isinstance(total, int):
            total_count = total
        elif isinstance(total, float) and total.is_integer():
            total_count = int(total)
        elif isinstance(total, str):
            try:
                total_count = int(total)
            except ValueError:
                total_count = offset + len(devices_data)
        else:
            total_count = offset + len(devices_data)
        return offset + len(devices_data) < max(total_count, 0)

    async def _fetch_device_page(self, *, page: int) -> tuple[list[DeviceRow], bool]:
        """Fetch one device page through the formal canonical contract."""
        offset = (page - 1) * _DEFAULT_DEVICE_PAGE_SIZE
        response = await self._client.get_devices(
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

        raw_devices: list[DeviceListItem] = []
        for row in devices_payload:
            if not isinstance(row, dict):
                raise RuntimeSnapshotRefreshRejectedError(
                    stage="page_row",
                    page=page,
                    cause_type=type(row).__name__,
                )
            raw_devices.append(row)

        devices_data = cast(list[DeviceRow], [dict(row) for row in raw_devices])
        return devices_data, self._canonical_page_has_more(
            offset=offset,
            devices_data=raw_devices,
            total=response.get("total"),
        )

    def __init__(
        self,
        *,
        client: SnapshotProtocolClient,
        device_identity_index: DeviceIdentityIndex,
        device_filter: DeviceFilter,
    ) -> None:
        """Initialize snapshot builder."""
        self._client = client
        self._contracts = client.contracts
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

    @staticmethod
    def _build_index_identity_aliases(
        normalized_row: DeviceRow,
        device: LiproDevice,
    ) -> set[str]:
        """Build the identity aliases used by runtime lookup indexes."""
        raw_identity_aliases = normalized_row.get("identityAliases")
        identity_aliases = (
            {
                alias
                for alias in raw_identity_aliases
                if isinstance(alias, str) and alias.strip()
            }
            if isinstance(raw_identity_aliases, list)
            else set()
        )
        identity_aliases.add(device.serial)
        if device.iot_device_id:
            identity_aliases.add(device.iot_device_id)
        return identity_aliases

    def _record_snapshot_device(
        self,
        *,
        normalized_row: DeviceRow,
        device: LiproDevice,
        devices: dict[str, LiproDevice],
        device_by_id: dict[str, LiproDevice],
        identity_mapping: dict[str, LiproDevice],
        iot_ids: list[str],
        group_ids: list[str],
        outlet_ids: list[str],
        cloud_serials: set[str],
        diagnostic_gateway_devices: dict[str, LiproDevice],
    ) -> None:
        """Record one normalized device into runtime snapshot buckets."""
        if device.capabilities.is_gateway:
            diagnostic_gateway_devices[device.serial] = device
            return

        devices[device.serial] = device
        device.extra_data["identity_aliases"] = [device.serial]

        for identity_alias in self._build_index_identity_aliases(normalized_row, device):
            device_by_id[identity_alias] = device
            identity_mapping[identity_alias] = device

        cloud_serials.add(device.serial)

        if device.is_group:
            if device.iot_device_id:
                group_ids.append(device.iot_device_id)
        elif device.capabilities.is_outlet:
            if device.iot_device_id:
                outlet_ids.append(device.iot_device_id)
        elif device.iot_device_id:
            iot_ids.append(device.iot_device_id)

    async def build_full_snapshot(
        self,
        *,
        max_pages: int = 50,
    ) -> FetchedDeviceSnapshot:
        """Build complete device snapshot from paginated API."""
        all_devices = await self._collect_snapshot_pages(max_pages=max_pages)

        devices: dict[str, LiproDevice] = {}
        device_by_id: dict[str, LiproDevice] = {}
        identity_mapping: dict[str, LiproDevice] = {}
        iot_ids: list[str] = []
        group_ids: list[str] = []
        outlet_ids: list[str] = []
        cloud_serials: set[str] = set()
        diagnostic_gateway_devices: dict[str, LiproDevice] = {}

        for page_number, device_data in all_devices:
            try:
                normalized_row = self._canonicalize_device_row(device_data)
                if not self._device_filter.is_device_included(normalized_row):
                    _LOGGER.debug("Device filtered out by configuration")
                    continue

                device = LiproDevice.from_api_data(cast(dict[str, object], normalized_row))
            except asyncio.CancelledError:
                raise
            except (RuntimeError, ValueError, TypeError, LookupError) as err:
                raise RuntimeSnapshotRefreshRejectedError(
                    stage="parse_device",
                    page=page_number,
                    device_ref=self._device_ref_from_row(device_data),
                    cause_type=type(err).__name__,
                ) from err

            self._record_snapshot_device(
                normalized_row=normalized_row,
                device=device,
                devices=devices,
                device_by_id=device_by_id,
                identity_mapping=identity_mapping,
                iot_ids=iot_ids,
                group_ids=group_ids,
                outlet_ids=outlet_ids,
                cloud_serials=cloud_serials,
                diagnostic_gateway_devices=diagnostic_gateway_devices,
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
    "RuntimeSnapshotRefreshFailure",
    "RuntimeSnapshotRefreshRejectedError",
    "SnapshotBuilder",
]
