"""Incremental device refresh strategy."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from custom_components.lipro.core.device import LiproDevice
    from custom_components.lipro.core.api import LiproClient

_LOGGER = logging.getLogger(__name__)


class IncrementalRefreshStrategy:
    """Handles incremental device state updates without full list refresh."""

    def __init__(self, *, client: LiproClient) -> None:
        """Initialize incremental refresh strategy.

        Args:
            client: API client for device queries
        """
        self._client = client

    async def refresh_device_states(
        self,
        *,
        iot_ids: list[str],
        group_ids: list[str],
        outlet_ids: list[str],
        devices: dict[str, LiproDevice],
        batch_optimizer: Any,  # DeviceBatchOptimizer to avoid circular import
    ) -> dict[str, dict[str, Any]]:
        """Refresh device states incrementally without full list fetch.

        Args:
            iot_ids: IoT device IDs to query
            group_ids: Group device IDs to query
            outlet_ids: Outlet device IDs to query
            devices: Current device snapshot
            batch_optimizer: Batch optimizer for splitting queries

        Returns:
            Dict mapping device_id to updated state data
        """
        updated_states: dict[str, dict[str, Any]] = {}

        # Query IoT devices in batches
        if iot_ids:
            for batch in batch_optimizer.split_into_batches(iot_ids):
                try:
                    response = await self._client.query_iot_devices(batch)
                    for device_data in response.get("data", []):
                        device_id = device_data.get("id")
                        if device_id:
                            updated_states[device_id] = device_data
                except Exception as err:  # noqa: BLE001
                    _LOGGER.debug(
                        "IoT device batch query failed (%s), skipping batch",
                        type(err).__name__,
                    )

        # Query group devices in batches
        if group_ids:
            for batch in batch_optimizer.split_into_batches(group_ids):
                try:
                    response = await self._client.query_group_devices(batch)
                    for device_data in response.get("data", []):
                        device_id = device_data.get("id")
                        if device_id:
                            updated_states[device_id] = device_data
                except Exception as err:  # noqa: BLE001
                    _LOGGER.debug(
                        "Group device batch query failed (%s), skipping batch",
                        type(err).__name__,
                    )

        # Query outlet devices in batches
        if outlet_ids:
            for batch in batch_optimizer.split_into_batches(outlet_ids):
                try:
                    response = await self._client.query_outlet_devices(batch)
                    for device_data in response.get("data", []):
                        device_id = device_data.get("id")
                        if device_id:
                            updated_states[device_id] = device_data
                except Exception as err:  # noqa: BLE001
                    _LOGGER.debug(
                        "Outlet device batch query failed (%s), skipping batch",
                        type(err).__name__,
                    )

        # Apply state updates to existing devices
        updated_count = 0
        for device_id, state_data in updated_states.items():
            device = devices.get(device_id)
            if device:
                device.update_from_api(state_data)
                updated_count += 1

        _LOGGER.debug(
            "Incremental refresh updated %d/%d devices",
            updated_count,
            len(updated_states),
        )

        return updated_states


__all__ = ["IncrementalRefreshStrategy"]
