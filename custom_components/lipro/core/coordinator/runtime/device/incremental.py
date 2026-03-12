"""Incremental device refresh strategy."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from custom_components.lipro.core.api import LiproClient
    from custom_components.lipro.core.device import LiproDevice

_LOGGER = logging.getLogger(__name__)


class IncrementalRefreshStrategy:
    """Handles incremental device state updates without full list refresh."""

    def __init__(
        self,
        *,
        client: LiproClient,
        device_resolver: Callable[[str], LiproDevice | None] | None = None,
    ) -> None:
        """Initialize incremental refresh strategy.

        Args:
            client: API client for device queries
            device_resolver: Optional unified device lookup for id-based responses
        """
        self._client = client
        self._device_resolver = device_resolver

    async def refresh_device_states(
        self,
        *,
        iot_ids: list[str],
        group_ids: list[str],
        outlet_ids: list[str],
        devices: dict[str, LiproDevice],
        batch_optimizer: Any,
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

        if iot_ids:
            for batch in batch_optimizer.split_into_batches(iot_ids):
                try:
                    response = await self._client.query_iot_devices(batch)
                    for device_data in response.get("data", []):
                        device_id = device_data.get("id")
                        if device_id:
                            updated_states[device_id] = device_data
                except Exception as err:
                    if isinstance(err, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
                        raise
                    _LOGGER.debug(
                        "IoT device batch query failed (%s), skipping batch",
                        type(err).__name__,
                    )

        if group_ids:
            for batch in batch_optimizer.split_into_batches(group_ids):
                try:
                    response = await self._client.query_group_devices(batch)
                    for device_data in response.get("data", []):
                        device_id = device_data.get("id")
                        if device_id:
                            updated_states[device_id] = device_data
                except Exception as err:
                    if isinstance(err, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
                        raise
                    _LOGGER.debug(
                        "Group device batch query failed (%s), skipping batch",
                        type(err).__name__,
                    )

        if outlet_ids:
            for batch in batch_optimizer.split_into_batches(outlet_ids):
                try:
                    response = await self._client.query_outlet_devices(batch)
                    for device_data in response.get("data", []):
                        device_id = device_data.get("id")
                        if device_id:
                            updated_states[device_id] = device_data
                except Exception as err:
                    if isinstance(err, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
                        raise
                    _LOGGER.debug(
                        "Outlet device batch query failed (%s), skipping batch",
                        type(err).__name__,
                    )

        updated_count = 0
        for device_id, state_data in updated_states.items():
            device = devices.get(device_id)
            if device is None and self._device_resolver is not None:
                device = self._device_resolver(device_id)
            if device is None:
                continue

            properties = state_data.get("properties", {})
            if properties:
                device.update_properties(properties)
            updated_count += 1

        _LOGGER.debug(
            "Incremental refresh updated %d/%d devices",
            updated_count,
            len(updated_states),
        )

        return updated_states


__all__ = ["IncrementalRefreshStrategy"]
