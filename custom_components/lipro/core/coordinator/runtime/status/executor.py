"""Status polling executor for running device status queries."""

from __future__ import annotations

import asyncio
import logging
from time import monotonic
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from ....device import LiproDevice

_LOGGER = logging.getLogger(__name__)


class StatusExecutor:
    """Execute device status queries with error handling and metrics."""

    def __init__(
        self,
        *,
        query_device_status: Callable[[list[str]], Coroutine[Any, Any, dict[str, dict[str, Any]]]],
        apply_properties_update: Callable[[LiproDevice, dict[str, Any], str], bool],
        get_device_by_id: Callable[[str], LiproDevice | None],
    ) -> None:
        """Initialize status executor.

        Args:
            query_device_status: Async function to query device status
            apply_properties_update: Function to apply property updates
            get_device_by_id: Function to look up devices
        """
        self._query_device_status = query_device_status
        self._apply_properties_update = apply_properties_update
        self._get_device_by_id = get_device_by_id

    async def execute_status_query(
        self,
        device_ids: list[str],
    ) -> dict[str, Any]:
        """Execute status query for a batch of devices.

        Args:
            device_ids: List of device IDs to query

        Returns:
            Execution metrics including duration and update count
        """
        if not device_ids:
            return {
                "duration": 0.0,
                "device_count": 0,
                "updated_count": 0,
                "error": None,
            }

        start = monotonic()
        updated_count = 0
        error: str | None = None

        try:
            status_data = await self._query_device_status(device_ids)

            for device_id, properties in status_data.items():
                device = self._get_device_by_id(device_id)
                if device is None:
                    continue

                changed = self._apply_properties_update(
                    device,
                    properties,
                    "rest_status",
                )
                if changed:
                    updated_count += 1

        except Exception as err:
            error = str(err)
            _LOGGER.warning(
                "Status query failed for %d devices: %s",
                len(device_ids),
                error,
            )

        duration = monotonic() - start

        return {
            "duration": duration,
            "device_count": len(device_ids),
            "updated_count": updated_count,
            "error": error,
        }

    async def execute_parallel_queries(
        self,
        batches: list[list[str]],
        *,
        concurrency: int = 3,
    ) -> list[dict[str, Any]]:
        """Execute multiple status queries in parallel.

        Args:
            batches: List of device ID batches
            concurrency: Maximum concurrent queries

        Returns:
            List of execution metrics for each batch
        """
        if not batches:
            return []

        semaphore = asyncio.Semaphore(concurrency)

        async def _execute_with_semaphore(batch: list[str]) -> dict[str, Any]:
            async with semaphore:
                return await self.execute_status_query(batch)

        results = await asyncio.gather(
            *[_execute_with_semaphore(batch) for batch in batches],
            return_exceptions=True,
        )

        metrics: list[dict[str, Any]] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                metrics.append({
                    "duration": 0.0,
                    "device_count": len(batches[i]),
                    "updated_count": 0,
                    "error": str(result),
                })
            else:
                metrics.append(result)

        return metrics


__all__ = ["StatusExecutor"]
