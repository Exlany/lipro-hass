"""Status polling executor for running device status queries."""

from __future__ import annotations

import asyncio
import logging
from time import monotonic
from typing import TYPE_CHECKING, cast

from ....api import LiproApiError, LiproAuthError, LiproConnectionError
from ...types import PropertyDict, StatusQueryMetrics

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from ....device import LiproDevice

_LOGGER = logging.getLogger(__name__)
_NON_FATAL_STATUS_QUERY_EXCEPTIONS = (
    LiproApiError,
    LiproConnectionError,
    OSError,
    RuntimeError,
    TimeoutError,
    ValueError,
)
_NON_FATAL_STATUS_APPLY_EXCEPTIONS = (KeyError, RuntimeError, TypeError, ValueError)


class StatusExecutor:
    """Execute device status queries with error handling and metrics."""

    def __init__(
        self,
        *,
        query_device_status: Callable[[list[str]], Awaitable[dict[str, PropertyDict]]],
        apply_properties_update: Callable[
            [LiproDevice, PropertyDict, str], Awaitable[bool]
        ],
        get_device_by_id: Callable[[str], LiproDevice | None],
    ) -> None:
        """Initialize status executor.

        Args:
            query_device_status: Async function to query device status
            apply_properties_update: Async function to apply property updates
            get_device_by_id: Function to look up devices
        """
        self._query_device_status = query_device_status
        self._apply_properties_update = apply_properties_update
        self._get_device_by_id = get_device_by_id

    @staticmethod
    def _empty_metrics() -> StatusQueryMetrics:
        return {
            "duration": 0.0,
            "device_count": 0,
            "updated_count": 0,
            "error": None,
        }

    @staticmethod
    def _query_failure_metrics(
        *,
        start: float,
        device_count: int,
        error: str,
    ) -> StatusQueryMetrics:
        return {
            "duration": monotonic() - start,
            "device_count": device_count,
            "updated_count": 0,
            "error": error,
            "apply_errors": None,
        }

    async def _apply_status_data(
        self,
        status_data: dict[str, PropertyDict],
    ) -> tuple[int, list[str]]:
        updated_count = 0
        apply_errors: list[str] = []

        for device_id, properties in status_data.items():
            device = self._get_device_by_id(device_id)
            if device is None:
                continue

            try:
                changed = await self._apply_properties_update(
                    device,
                    properties,
                    "rest_status",
                )
            except _NON_FATAL_STATUS_APPLY_EXCEPTIONS as err:
                apply_errors.append(f"{device_id}:{err}")
                _LOGGER.warning(
                    "Status apply failed for %s: %s",
                    device_id,
                    type(err).__name__,
                )
                continue

            if changed:
                updated_count += 1

        return updated_count, apply_errors

    async def execute_status_query(
        self,
        device_ids: list[str],
    ) -> StatusQueryMetrics:
        """Execute status query for a batch of devices.

        Args:
            device_ids: List of device IDs to query

        Returns:
            Execution metrics including duration and update count
        """
        if not device_ids:
            return self._empty_metrics()

        start = monotonic()

        try:
            status_data = await self._query_device_status(device_ids)
        except LiproAuthError:
            raise
        except _NON_FATAL_STATUS_QUERY_EXCEPTIONS as err:
            error = str(err)
            _LOGGER.warning(
                "Status query failed for %d devices: %s",
                len(device_ids),
                error,
            )
            return self._query_failure_metrics(
                start=start,
                device_count=len(device_ids),
                error=error,
            )

        updated_count, apply_errors = await self._apply_status_data(status_data)

        return {
            "duration": monotonic() - start,
            "device_count": len(device_ids),
            "updated_count": updated_count,
            "error": None,
            "apply_errors": apply_errors or None,
        }

    async def execute_parallel_queries(
        self,
        batches: list[list[str]],
        *,
        concurrency: int = 3,
    ) -> list[StatusQueryMetrics]:
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

        async def _execute_with_semaphore(batch: list[str]) -> StatusQueryMetrics:
            async with semaphore:
                return await self.execute_status_query(batch)

        results = await asyncio.gather(
            *[_execute_with_semaphore(batch) for batch in batches],
            return_exceptions=True,
        )

        metrics: list[StatusQueryMetrics] = []
        for i, result in enumerate(results):
            if isinstance(result, asyncio.CancelledError):
                raise result
            if isinstance(result, Exception):
                failure_metrics: StatusQueryMetrics = {
                    "duration": 0.0,
                    "device_count": len(batches[i]),
                    "updated_count": 0,
                    "error": str(result),
                }
                metrics.append(failure_metrics)
            else:
                metrics.append(cast(StatusQueryMetrics, result))

        return metrics


__all__ = ["StatusExecutor"]
