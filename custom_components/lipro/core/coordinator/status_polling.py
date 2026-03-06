"""Coordinator polling/update loop for device status, power, and product configs."""

from __future__ import annotations

import asyncio
import logging
from time import monotonic
from typing import Any, Final

from homeassistant.helpers.update_coordinator import UpdateFailed

from ..api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from ..device import LiproDevice, parse_properties_list
from ..device.group_status import resolve_mesh_group_lookup_ids
from ..utils.log_safety import safe_error_placeholder
from ..utils.redaction import redact_identifier
from .auth_issues import _CoordinatorAuthIssuesMixin
from .outlet_power import apply_outlet_power_info, should_reraise_outlet_power_error
from .runtime.group_lookup_runtime import compute_group_lookup_mapping_decision
from .runtime.outlet_power_runtime import (
    query_outlet_power as query_outlet_power_runtime,
    query_single_outlet_power as query_single_outlet_power_runtime,
    resolve_outlet_power_cycle_size as resolve_outlet_power_cycle_size_runtime,
)
from .runtime.product_config_runtime import (
    apply_product_config as apply_product_config_runtime,
    index_product_configs as index_product_configs_runtime,
    match_product_config as match_product_config_runtime,
)

_LOGGER = logging.getLogger(__name__)

# Cap concurrent per-outlet power-info requests to avoid API rate limiting.
_OUTLET_POWER_QUERY_CONCURRENCY: Final[int] = 5

# When many outlets exist, query power info in rotating slices to avoid large
# bursts on each power interval tick.
_OUTLET_POWER_QUERY_MAX_DEVICES_PER_CYCLE: Final[int] = 10
_OUTLET_POWER_TARGET_FULL_CYCLE_COUNT: Final[int] = 4


class _CoordinatorStatusPollingMixin(_CoordinatorAuthIssuesMixin):
    """Mixin: _async_update_data and status/product-config polling helpers."""

    async def _async_update_data(self) -> dict[str, LiproDevice]:
        """Fetch data from API."""
        try:
            await self._async_ensure_authenticated()

            if self._should_refresh_device_list():
                self._force_device_refresh = False
                await self._fetch_devices()
                await self._load_product_configs()

            await self._update_device_status()

            self._schedule_mqtt_setup_if_needed()
            self._check_mqtt_disconnect_notification()

            return self._devices

        except (
            LiproRefreshTokenExpiredError,
            LiproAuthError,
            LiproConnectionError,
            LiproApiError,
        ) as err:
            await self._raise_update_data_error(err)

        raise UpdateFailed("Unexpected update failure")

    async def _load_product_configs(self) -> None:
        """Load product configurations and apply color temp ranges to devices."""
        if self._product_configs_by_id or self._product_configs:
            self._apply_product_configs_to_devices(
                self._product_configs_by_id,
                self._product_configs,
            )
            return

        try:
            configs = await self.client.get_product_configs()
            _LOGGER.debug("Loaded %d product configurations", len(configs))

            configs_by_id, configs_by_iot_name = index_product_configs_runtime(configs)
            self._product_configs_by_id = configs_by_id
            self._product_configs = configs_by_iot_name
            self._apply_product_configs_to_devices(configs_by_id, configs_by_iot_name)

        except LiproApiError as err:
            _LOGGER.warning(
                "Failed to load product configs (%s)",
                safe_error_placeholder(err),
            )

    def _apply_product_configs_to_devices(
        self,
        configs_by_id: dict[int, dict[str, Any]],
        configs_by_iot_name: dict[str, dict[str, Any]],
    ) -> None:
        """Match and apply cached product-config overrides to all devices."""
        for device in self._devices.values():
            matched = self._match_product_config(
                device,
                configs_by_id,
                configs_by_iot_name,
            )
            if matched:
                self._apply_product_config(device, matched)

    def _match_product_config(
        self,
        device: LiproDevice,
        configs_by_id: dict[int, dict[str, Any]],
        configs_by_iot_name: dict[str, dict[str, Any]],
    ) -> dict[str, Any] | None:
        """Match one device to its best product config."""
        return match_product_config_runtime(
            device,
            configs_by_id=configs_by_id,
            configs_by_iot_name=configs_by_iot_name,
            logger=_LOGGER,
        )

    def _apply_product_config(
        self, device: LiproDevice, config: dict[str, Any]
    ) -> None:
        """Apply matched product-config overrides to runtime device model."""
        apply_product_config_runtime(device, config, logger=_LOGGER)

    async def _update_device_status(self) -> None:
        """Update status for all devices."""
        status_tasks: list[asyncio.Task[Any] | asyncio.Future[Any]] = []

        if self._iot_ids_to_query:
            status_tasks.append(
                self._track_background_task(self._query_device_status())
            )
        if self._group_ids_to_query:
            status_tasks.append(self._track_background_task(self._query_group_status()))
        if (
            self._power_monitoring_enabled
            and self._outlet_ids_to_query
            and self._should_query_power()
        ):
            status_tasks.append(self._track_background_task(self._query_outlet_power()))

        if status_tasks:
            await asyncio.gather(*status_tasks)

        connect_ids = self._resolve_connect_status_query_ids()
        if connect_ids:
            await self._query_connect_status(connect_ids)

    def _should_query_power(self) -> bool:
        """Return True when power query interval has elapsed."""
        now = monotonic()
        if now - self._last_power_query_time >= self._power_query_interval:
            self._last_power_query_time = now
            return True
        return False

    async def _query_device_status(self) -> None:
        """Query status for individual devices."""
        status_list = await self.client.query_device_status(
            self._iot_ids_to_query,
            max_devices_per_query=self._state_status_batch_size,
            on_batch_metric=self._record_state_batch_metric,
        )
        self._adapt_state_batch_size()

        for status_data in status_list:
            self._apply_device_status_row(status_data)

    def _apply_device_status_row(self, status_data: dict[str, Any]) -> None:
        """Apply one device-status row to a mapped device."""
        device_id = status_data.get("deviceId")
        if not device_id:
            return

        device = self.get_device_by_id(device_id)
        if not device:
            return

        raw_properties = status_data.get("properties")
        if raw_properties:
            properties = parse_properties_list(raw_properties)
            self._apply_properties_update(device, properties)

    async def _query_group_status(self) -> None:
        """Query status for mesh groups."""
        status_list = await self.client.query_mesh_group_status(
            self._group_ids_to_query,
        )

        for status_data in status_list:
            self._apply_group_status_row(status_data)

    def _apply_group_status_row(self, status_data: dict[str, Any]) -> None:
        """Apply one mesh group status row to device mappings and properties."""
        group_id = status_data.get("groupId")
        if not group_id:
            _LOGGER.warning(
                "Missing groupId in mesh group status response: %s",
                list(status_data.keys()),
            )
            return

        device = self._devices.get(group_id)
        if not device:
            _LOGGER.debug(
                "Unknown group in status response: %s",
                redact_identifier(group_id) or "***",
            )
            return

        self._apply_group_lookup_mappings(device, status_data)

        raw_properties = status_data.get("properties")
        if raw_properties:
            properties = parse_properties_list(raw_properties)
            self._apply_properties_update(device, properties)

    def _apply_group_lookup_mappings(
        self,
        device: LiproDevice,
        status_data: dict[str, Any],
    ) -> None:
        """Update lookup IDs and group-member metadata for a mesh group device."""
        lookup_ids = resolve_mesh_group_lookup_ids(status_data)
        decision = compute_group_lookup_mapping_decision(
            previous_gateway_id=device.extra_data.get("gateway_device_id"),
            current_gateway_id=lookup_ids.gateway_id,
            previous_member_lookup_ids=device.extra_data.get(
                "group_member_lookup_ids", []
            ),
            current_member_lookup_ids=lookup_ids.member_lookup_ids,
            member_ids=lookup_ids.member_ids,
        )
        if decision.gateway_unregister_id:
            self._device_identity_index.unregister(
                decision.gateway_unregister_id,
                device=device,
            )

        if decision.gateway_extra_data_value:
            device.extra_data["gateway_device_id"] = decision.gateway_extra_data_value
            self._device_identity_index.register(
                decision.gateway_extra_data_value, device
            )
        else:
            device.extra_data.pop("gateway_device_id", None)

        for stale_lookup_id in decision.member_unregister_ids:
            self._device_identity_index.unregister(
                stale_lookup_id,
                device=device,
            )

        for member_lookup_id in decision.member_register_ids:
            self._device_identity_index.register(member_lookup_id, device)
        device.extra_data["group_member_ids"] = decision.member_ids_extra_data
        device.extra_data["group_member_lookup_ids"] = (
            decision.member_lookup_ids_extra_data
        )
        device.extra_data["group_member_count"] = decision.member_count

    async def _query_outlet_power(self) -> None:
        """Query power information for outlet devices."""
        self._outlet_power_round_robin_index = await query_outlet_power_runtime(
            outlet_ids_to_query=self._outlet_ids_to_query,
            round_robin_index=self._outlet_power_round_robin_index,
            resolve_cycle_size=self._resolve_outlet_power_cycle_size,
            fetch_outlet_power_info=self.client.fetch_outlet_power_info,
            get_device_by_id=self.get_device_by_id,
            apply_outlet_power_info=apply_outlet_power_info,
            should_reraise_outlet_power_error=should_reraise_outlet_power_error,
            logger=_LOGGER,
            concurrency=_OUTLET_POWER_QUERY_CONCURRENCY,
        )

    @staticmethod
    def _resolve_outlet_power_cycle_size(total_devices: int) -> int:
        """Resolve per-cycle outlet power query size with bounded dynamic scaling."""
        return resolve_outlet_power_cycle_size_runtime(
            total_devices,
            max_devices_per_cycle=_OUTLET_POWER_QUERY_MAX_DEVICES_PER_CYCLE,
            target_full_cycle_count=_OUTLET_POWER_TARGET_FULL_CYCLE_COUNT,
        )

    async def _query_single_outlet_power(self, device_id: str) -> None:
        """Query and apply power info for one outlet device."""
        await query_single_outlet_power_runtime(
            device_id=device_id,
            fetch_outlet_power_info=self.client.fetch_outlet_power_info,
            get_device_by_id=self.get_device_by_id,
            apply_outlet_power_info=apply_outlet_power_info,
            should_reraise_outlet_power_error=should_reraise_outlet_power_error,
            logger=_LOGGER,
        )

    async def async_refresh_devices(self) -> None:
        """Force refresh of device list on next refresh tick."""
        self._force_device_refresh = True
        self._product_configs_by_id.clear()
        self._product_configs.clear()
        await self.async_refresh()


__all__ = ["_CoordinatorStatusPollingMixin"]
