"""Device batch query optimization logic."""

from __future__ import annotations

import logging
from typing import Final

from custom_components.lipro.const.api import MAX_DEVICES_PER_QUERY

_LOGGER = logging.getLogger(__name__)

# Defensive cap for malformed pagination responses that never terminate.
MAX_DEVICE_LIST_PAGES: Final[int] = 50


class DeviceBatchOptimizer:
    """Optimizes device queries into efficient batches."""

    def __init__(
        self,
        *,
        max_devices_per_query: int = MAX_DEVICES_PER_QUERY,
        max_pages: int = MAX_DEVICE_LIST_PAGES,
    ) -> None:
        """Initialize batch optimizer.

        Args:
            max_devices_per_query: Maximum device IDs per API call
            max_pages: Maximum pagination pages to prevent infinite loops
        """
        self._max_devices_per_query = max_devices_per_query
        self._max_pages = max_pages

    def split_into_batches(self, device_ids: list[str]) -> list[list[str]]:
        """Split device ID list into API-compatible batches.

        Args:
            device_ids: Full list of device IDs to query

        Returns:
            List of batches, each within max_devices_per_query limit
        """
        if not device_ids:
            return []

        batches: list[list[str]] = []
        for i in range(0, len(device_ids), self._max_devices_per_query):
            batch = device_ids[i : i + self._max_devices_per_query]
            batches.append(batch)

        _LOGGER.debug(
            "Split %d device IDs into %d batch(es)",
            len(device_ids),
            len(batches),
        )
        return batches

    def validate_page_count(self, page_num: int) -> bool:
        """Check if pagination is within safe limits.

        Args:
            page_num: Current page number (1-indexed)

        Returns:
            True if within limits, False if exceeded
        """
        if page_num > self._max_pages:
            _LOGGER.error(
                "Device list pagination exceeded %d pages, aborting to prevent infinite loop",
                self._max_pages,
            )
            return False
        return True

    def estimate_query_count(
        self,
        *,
        iot_ids: list[str],
        group_ids: list[str],
        outlet_ids: list[str],
    ) -> int:
        """Estimate total API queries needed for device refresh.

        Args:
            iot_ids: IoT device IDs
            group_ids: Group device IDs
            outlet_ids: Outlet device IDs

        Returns:
            Estimated number of API calls
        """
        total_devices = len(iot_ids) + len(group_ids) + len(outlet_ids)
        if total_devices == 0:
            return 0

        # Each category needs separate batches
        iot_batches = (len(iot_ids) + self._max_devices_per_query - 1) // self._max_devices_per_query
        group_batches = (len(group_ids) + self._max_devices_per_query - 1) // self._max_devices_per_query
        outlet_batches = (len(outlet_ids) + self._max_devices_per_query - 1) // self._max_devices_per_query

        return iot_batches + group_batches + outlet_batches


__all__ = [
    "MAX_DEVICE_LIST_PAGES",
    "DeviceBatchOptimizer",
]
