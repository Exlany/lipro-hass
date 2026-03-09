"""Device refresh and reconciliation mixin for the coordinator."""

from __future__ import annotations

import logging
from time import monotonic
from typing import Any, Final

from homeassistant.helpers import area_registry as ar, device_registry as dr

from ...const.api import MAX_DEVICES_PER_QUERY
from ...const.base import DOMAIN
from ..api import LiproApiError
from ..device import LiproDevice
from .device_list_snapshot import (
    FetchedDeviceSnapshot,
    build_fetched_device_snapshot,
    is_device_included_by_filter,
    plan_stale_device_reconciliation,
)
from .device_registry_sync import (
    collect_registry_serials_for_entry,
    remove_stale_registry_devices,
    sync_device_room_assignments,
)
from .mqtt.messages import _MqttMixin
from .runtime.coordinator_runtime import (
    should_refresh_device_list as should_refresh_device_list_runtime,
)
from .runtime.room_sync_runtime import (
    normalize_room_name as normalize_room_name_runtime,
    resolve_room_area_target_name as resolve_room_area_target_name_runtime,
)

_LOGGER = logging.getLogger(__name__)

# Number of consecutive full-device-list fetches a device can be missing
# before being removed from HA device registry.
_STALE_DEVICE_REMOVE_THRESHOLD: Final[int] = 3

# Periodic full device-list refresh to discover newly paired devices.
_DEVICE_LIST_REFRESH_INTERVAL_SECONDS: Final[int] = 600

# Defensive cap for malformed pagination responses that never terminate.
_MAX_DEVICE_LIST_PAGES: Final[int] = 50

# Coalesce reload triggers caused by device-list changes (new devices discovered,
# stale devices removed) to avoid reload storms under cloud jitter.
_ENTRY_RELOAD_DEBOUNCE_SECONDS: Final[float] = 5.0
_ENTRY_RELOAD_MIN_INTERVAL_SECONDS: Final[float] = 60.0


class _DeviceRefreshMixin(_MqttMixin):
    """Coordinator mixin for full device-list refresh and stale reconciliation."""

    def _request_entry_reload(self, *, reason: str) -> bool:
        """Request a debounced config-entry reload and return True when queued.

        Prefer scheduling via Home Assistant's ``async_schedule_reload`` to avoid
        deadlocks where a reload task cancels itself during unload.
        """
        if self.config_entry is None:
            return False

        self._entry_reload_reasons.add(reason)

        if self._entry_reload_handle is not None:
            return False

        if not self.hass.loop.is_running():
            self._flush_entry_reload()
            return True

        delay = _ENTRY_RELOAD_DEBOUNCE_SECONDS
        now = monotonic()
        if self._last_entry_reload_at > 0.0:
            elapsed = now - self._last_entry_reload_at
            if elapsed < _ENTRY_RELOAD_MIN_INTERVAL_SECONDS:
                delay = max(delay, _ENTRY_RELOAD_MIN_INTERVAL_SECONDS - elapsed)

        if delay <= 0:
            self._flush_entry_reload()
            return True

        self._entry_reload_handle = self.hass.loop.call_later(
            delay,
            self._flush_entry_reload,
        )
        return True

    def _flush_entry_reload(self) -> None:
        """Flush one debounced config-entry reload request."""
        self._entry_reload_handle = None

        if self.config_entry is None:
            self._entry_reload_reasons.clear()
            return

        now = monotonic()
        if (
            self._last_entry_reload_at > 0.0
            and now - self._last_entry_reload_at < _ENTRY_RELOAD_MIN_INTERVAL_SECONDS
        ):
            if not self.hass.loop.is_running():
                self._entry_reload_reasons.clear()
                return

            remaining = _ENTRY_RELOAD_MIN_INTERVAL_SECONDS - (
                now - self._last_entry_reload_at
            )
            self._entry_reload_handle = self.hass.loop.call_later(
                remaining,
                self._flush_entry_reload,
            )
            return

        reasons = sorted(self._entry_reload_reasons)
        self._entry_reload_reasons.clear()
        self._last_entry_reload_at = now

        _LOGGER.debug(
            "Scheduling entry reload (reasons=%s)",
            ",".join(reasons) if reasons else "unknown",
        )
        self.hass.config_entries.async_schedule_reload(self.config_entry.entry_id)

    def _should_refresh_device_list(self) -> bool:
        """Return True when a full device-list refresh should run."""
        return should_refresh_device_list_runtime(
            has_devices=bool(self._devices),
            force_device_refresh=self._force_device_refresh,
            last_device_refresh_at=self._last_device_refresh_at,
            now=monotonic(),
            refresh_interval_seconds=_DEVICE_LIST_REFRESH_INTERVAL_SECONDS,
        )

    async def _fetch_devices(self) -> None:
        """Fetch all devices from API with pagination."""
        _LOGGER.debug("Fetching device list")

        previous_devices = self._devices
        previous_serials = set(previous_devices)
        previous_cloud_serials = self._cloud_serials_last_seen or previous_serials
        devices_data = await self._fetch_all_device_pages()
        snapshot = build_fetched_device_snapshot(
            devices_data,
            device_filter=self._device_row_passes_filter
            if self._device_filter_enabled
            else None,
        )
        self._apply_fetched_device_snapshot(snapshot)
        current_cloud_serials = snapshot.cloud_serials
        self._cloud_serials_last_seen = current_cloud_serials
        self._sync_device_room_assignments(previous_devices)
        self._last_device_refresh_at = monotonic()
        self._force_connect_status_refresh = True
        self._schedule_reload_for_added_devices(previous_serials)
        await self._record_devices_for_anonymous_share()
        await self._reconcile_stale_devices(
            previous_cloud_serials,
            current_serials=current_cloud_serials,
        )

        if self._mqtt_client and self._mqtt_connected:
            await self._sync_mqtt_subscriptions()

    def _device_row_passes_filter(self, device_data: dict[str, Any]) -> bool:
        """Return True when one raw device row passes configured filters."""
        return is_device_included_by_filter(device_data, self._device_filter_config)

    def _schedule_reload_for_added_devices(
        self,
        previous_serials: set[str],
    ) -> None:
        """Reload config entry when new devices are discovered after initial setup."""
        if not previous_serials or self.config_entry is None:
            return

        current_serials = set(self._devices)
        added_serials = current_serials - previous_serials
        if not added_serials:
            return

        registry_serials = collect_registry_serials_for_entry(
            device_registry=dr.async_get(self.hass),
            config_entry_id=self.config_entry.entry_id,
            domain=DOMAIN,
        )
        truly_new_serials = added_serials - registry_serials
        if not truly_new_serials:
            _LOGGER.debug(
                "Skipping reload: %d added device(s) already known in registry",
                len(added_serials),
            )
            return

        if self._request_entry_reload(reason="devices_added"):
            _LOGGER.info(
                "Discovered %d new Lipro device(s), queueing entry reload",
                len(truly_new_serials),
            )

    @staticmethod
    def _parse_device_list_page(
        result: Any,
        *,
        limit: int,
        logger: logging.Logger = _LOGGER,
    ) -> tuple[list[dict[str, Any]], bool]:
        """Parse one devices page payload from API.

        Returns:
            (devices, has_more)
        """
        if not isinstance(result, dict):
            msg = (
                "Malformed device list response: expected object, "
                f"got {type(result).__name__}"
            )
            raise LiproApiError(msg)

        raw_page = result.get("devices", [])
        if raw_page is None:
            raw_page = []
        if not isinstance(raw_page, list):
            msg = (
                "Malformed device list payload: expected devices list, "
                f"got {type(raw_page).__name__}"
            )
            raise LiproApiError(msg)

        page = [item for item in raw_page if isinstance(item, dict)]
        if len(page) != len(raw_page):
            logger.debug(
                "Skipping %d malformed device rows from API payload",
                len(raw_page) - len(page),
            )

        has_more = len(raw_page) >= limit
        return page, has_more

    async def _fetch_all_device_pages(self) -> list[dict[str, Any]]:
        """Fetch full device list from paginated API responses."""
        devices_data: list[dict[str, Any]] = []
        offset = 0
        page_count = 0

        while True:
            if page_count >= _MAX_DEVICE_LIST_PAGES:
                msg = (
                    "Malformed device list response: pagination exceeded "
                    f"{_MAX_DEVICE_LIST_PAGES} pages"
                )
                raise LiproApiError(msg)

            result: Any = await self.client.get_devices(
                offset=offset,
                limit=MAX_DEVICES_PER_QUERY,
            )
            page_count += 1

            page, has_more = self._parse_device_list_page(
                result,
                limit=MAX_DEVICES_PER_QUERY,
            )
            devices_data.extend(page)
            if not has_more:
                return devices_data
            offset += MAX_DEVICES_PER_QUERY

    def _apply_fetched_device_snapshot(self, snapshot: FetchedDeviceSnapshot) -> None:
        """Apply refreshed device snapshot atomically."""
        self._devices = snapshot.devices
        self._diagnostic_gateway_devices = snapshot.diagnostic_gateway_devices
        self._device_identity_index.replace(snapshot.device_by_id)
        self._iot_ids_to_query = snapshot.iot_ids
        self._group_ids_to_query = snapshot.group_ids
        self._outlet_ids_to_query = snapshot.outlet_ids

        _LOGGER.info(
            "Fetched %d devices (%d groups, %d individual, %d outlets)",
            len(self._devices),
            len(self._group_ids_to_query),
            len(self._iot_ids_to_query),
            len(self._outlet_ids_to_query),
        )

    @staticmethod
    def _normalize_room_name(room_name: str | None) -> str | None:
        """Normalize room names from cloud payloads to comparable values."""
        return normalize_room_name_runtime(room_name)

    def _sync_device_room_assignments(
        self, previous_devices: dict[str, LiproDevice]
    ) -> None:
        """Best-effort sync of cloud room changes into HA device registry areas."""
        if not previous_devices:
            return

        try:
            sync_device_room_assignments(
                devices=self._devices,
                previous_devices=previous_devices,
                room_area_sync_force=self._room_area_sync_force,
                domain=DOMAIN,
                device_registry=dr.async_get(self.hass),
                area_registry=ar.async_get(self.hass),
                normalize_room_name=self._normalize_room_name,
                resolve_room_area_target_name=resolve_room_area_target_name_runtime,
                logger=_LOGGER,
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug(
                "Room/area registry sync failed, skipping (%s)",
                type(err).__name__,
            )

    async def _record_devices_for_anonymous_share(self) -> None:
        """Record fetched devices for anonymous diagnostics sharing."""
        share_manager = self._get_anonymous_share_manager()
        if not share_manager.is_enabled:
            return

        await share_manager.async_ensure_loaded()
        share_manager.record_devices(list(self._devices.values()))

    async def _reconcile_stale_devices(
        self,
        previous_serials: set[str],
        *,
        current_serials: set[str] | None = None,
    ) -> None:
        """Remove devices missing for consecutive full refresh cycles."""
        tracked_serials = set(self._devices)
        self._prune_runtime_state_for_devices(tracked_serials)

        reconcile_current_serials = (
            tracked_serials if current_serials is None else current_serials
        )
        reconcile_previous_serials = previous_serials
        if (
            not reconcile_previous_serials
            and not self._missing_device_cycles
            and self.config_entry is not None
        ):
            # Cold-start bootstrap: use registry identifiers as stale baseline.
            reconcile_previous_serials = collect_registry_serials_for_entry(
                device_registry=dr.async_get(self.hass),
                config_entry_id=self.config_entry.entry_id,
                domain=DOMAIN,
            )

        reconcile_plan = plan_stale_device_reconciliation(
            previous_serials=reconcile_previous_serials,
            current_serials=reconcile_current_serials,
            missing_cycles=self._missing_device_cycles,
            remove_threshold=_STALE_DEVICE_REMOVE_THRESHOLD,
        )
        self._missing_device_cycles = reconcile_plan.missing_cycles

        if not reconcile_plan.removable_serials:
            return

        await self._async_remove_stale_devices(reconcile_plan.removable_serials)
        for serial in reconcile_plan.removable_serials:
            self._missing_device_cycles.pop(serial, None)

        for serial in reconcile_plan.removable_serials:
            entities = self._entities_by_device.pop(serial, [])
            for entity in entities:
                unique_id = getattr(entity, "unique_id", None)
                if unique_id and self._entities.get(unique_id) is entity:
                    self._entities.pop(unique_id, None)

        if self._request_entry_reload(reason="stale_devices_removed"):
            _LOGGER.info(
                "Removed %d stale Lipro device(s), queueing entry reload",
                len(reconcile_plan.removable_serials),
            )

    async def _async_remove_stale_devices(self, stale_serials: set[str]) -> None:
        """Remove devices that no longer exist in the cloud.

        Args:
            stale_serials: Set of device serial numbers that are no longer present.

        """
        if not self.config_entry:
            return

        try:
            remove_stale_registry_devices(
                stale_serials=stale_serials,
                domain=DOMAIN,
                device_registry=dr.async_get(self.hass),
                logger=_LOGGER,
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug(
                "Stale device registry cleanup failed, skipping (%s)",
                type(err).__name__,
            )


__all__ = ["_DeviceRefreshMixin"]
