"""Runtime helpers for outlet power querying."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import logging
import math
from typing import Any

from ..api import LiproApiError


def resolve_outlet_power_cycle_size(
    total_devices: int,
    *,
    max_devices_per_cycle: int,
    target_full_cycle_count: int,
) -> int:
    """Resolve per-cycle outlet power query size with bounded dynamic scaling."""
    if total_devices <= 0:
        return 0
    static_limit = min(total_devices, max_devices_per_cycle)
    dynamic_limit = math.ceil(total_devices / target_full_cycle_count)
    return min(total_devices, max(static_limit, dynamic_limit))


async def query_outlet_power(
    *,
    outlet_ids_to_query: list[str],
    round_robin_index: int,
    resolve_cycle_size: Callable[[int], int],
    query_single_outlet_power: Callable[[str], Awaitable[None]],
    concurrency: int,
) -> int:
    """Query outlet power info in bounded concurrent slices.

    Returns the updated round-robin index to persist in the coordinator.
    """
    if not outlet_ids_to_query:
        return round_robin_index

    device_ids = list(outlet_ids_to_query)
    if not device_ids:
        return round_robin_index

    updated_index = round_robin_index

    max_devices = resolve_cycle_size(len(device_ids))
    if len(device_ids) > max_devices:
        start = round_robin_index % len(device_ids)
        end = start + max_devices
        if end <= len(device_ids):
            device_ids = device_ids[start:end]
        else:
            device_ids = device_ids[start:] + device_ids[: end % len(device_ids)]
        updated_index = (start + max_devices) % len(outlet_ids_to_query)

    batch_size = min(concurrency, len(device_ids))
    for start in range(0, len(device_ids), batch_size):
        await asyncio.gather(
            *(
                query_single_outlet_power(did)
                for did in device_ids[start : start + batch_size]
            ),
        )

    return updated_index


async def query_single_outlet_power(
    *,
    device_id: str,
    fetch_outlet_power_info: Callable[[list[str]], Awaitable[dict[str, Any]]],
    get_device_by_id: Callable[[Any], Any],
    apply_outlet_power_info: Callable[[Any, dict[str, Any]], bool],
    should_reraise_outlet_power_error: Callable[[LiproApiError], bool],
    logger: logging.Logger,
) -> None:
    """Query and apply power info for one outlet device."""
    try:
        power_data = await fetch_outlet_power_info([device_id])
        if not power_data:
            return
        device = get_device_by_id(device_id)
        if device is not None and apply_outlet_power_info(device, power_data):
            logger.debug(
                "Updated power info for %s: nowPower=%s",
                device.name,
                power_data.get("nowPower"),
            )
    except LiproApiError as err:
        if should_reraise_outlet_power_error(err):
            raise
        logger.debug("Failed to query power for %s: %s", device_id, err)
