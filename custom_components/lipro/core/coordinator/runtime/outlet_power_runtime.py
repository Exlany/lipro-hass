"""Runtime helpers for outlet power querying."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import logging
import math
from typing import TYPE_CHECKING

from ...api import LiproApiError
from ..types import OutletPowerData, PropertyDict

if TYPE_CHECKING:
    from ...device import LiproDevice


def _normalize_device_id(value: object) -> str | None:
    """Normalize a device identifier for case/whitespace tolerant matching."""
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return normalized.lower()


def _normalize_single_outlet_power_payload(
    payload: object,
    *,
    requested_id: str,
) -> PropertyDict | None:
    """Normalize one power-info payload into a single device mapping payload."""
    normalized_requested_id = _normalize_device_id(requested_id)
    if normalized_requested_id is None:
        return None

    if isinstance(payload, dict):
        nested = payload.get(normalized_requested_id)
        if isinstance(nested, dict):
            return nested
        nested = payload.get(requested_id)
        if isinstance(nested, dict):
            return nested
        return payload or None

    if isinstance(payload, list):
        rows = [row for row in payload if isinstance(row, dict)]
        if not rows:
            return None
        return rows[0] if len(rows) == 1 else {"data": rows}

    return None


def resolve_outlet_power_cycle_size(
    total_devices: int,
    *,
    max_devices_per_cycle: int,
    target_full_cycle_count: int,
) -> int:
    """Resolve per-cycle outlet power query size.

    Keep single-cycle request pressure bounded by ``max_devices_per_cycle``
    while still allowing smaller slices for very large fleets.
    """
    if total_devices <= 0:
        return 0

    static_limit = min(total_devices, max_devices_per_cycle)
    if total_devices <= max_devices_per_cycle:
        return static_limit
    if target_full_cycle_count <= 0:
        return static_limit

    dynamic_limit = math.ceil(total_devices / target_full_cycle_count)
    return max(1, min(static_limit, dynamic_limit))


async def query_outlet_power(
    *,
    outlet_ids_to_query: list[str],
    round_robin_index: int,
    resolve_cycle_size: Callable[[int], int],
    fetch_outlet_power_info: Callable[[str], Awaitable[object]],
    get_device_by_id: Callable[[object], LiproDevice | None],
    apply_outlet_power_info: Callable[[LiproDevice, PropertyDict], bool],
    should_reraise_outlet_power_error: Callable[[LiproApiError], bool],
    logger: logging.Logger,
    concurrency: int,
) -> int:
    """Query outlet power info in bounded concurrent slices.

    The cloud endpoint accepts one ``deviceId`` per request, so runtime-level
    bounded concurrency is the real batching mechanism.
    """
    if not outlet_ids_to_query:
        return round_robin_index

    outlet_ids = list(outlet_ids_to_query)
    if not outlet_ids:
        return round_robin_index

    updated_index = round_robin_index

    max_devices = resolve_cycle_size(len(outlet_ids))
    if len(outlet_ids) > max_devices:
        start = round_robin_index % len(outlet_ids)
        end = start + max_devices
        if end <= len(outlet_ids):
            outlet_ids = outlet_ids[start:end]
        else:
            outlet_ids = outlet_ids[start:] + outlet_ids[: end % len(outlet_ids)]
        updated_index = (start + max_devices) % len(outlet_ids_to_query)

    async def _query_single(outlet_id: str) -> None:
        await query_single_outlet_power(
            device_id=outlet_id,
            fetch_outlet_power_info=fetch_outlet_power_info,
            get_device_by_id=get_device_by_id,
            apply_outlet_power_info=apply_outlet_power_info,
            should_reraise_outlet_power_error=should_reraise_outlet_power_error,
            logger=logger,
        )

    batch_size = max(1, min(concurrency, len(outlet_ids)))
    for start in range(0, len(outlet_ids), batch_size):
        await asyncio.gather(
            *(
                _query_single(outlet_id)
                for outlet_id in outlet_ids[start : start + batch_size]
            ),
        )

    return updated_index


async def query_single_outlet_power(
    *,
    device_id: str,
    fetch_outlet_power_info: Callable[[str], Awaitable[object]],
    get_device_by_id: Callable[[object], LiproDevice | None],
    apply_outlet_power_info: Callable[[LiproDevice, PropertyDict], bool],
    should_reraise_outlet_power_error: Callable[[LiproApiError], bool],
    logger: logging.Logger,
) -> None:
    """Query and apply power info for one outlet device."""
    normalized_id = _normalize_device_id(device_id)
    if normalized_id is None:
        return

    try:
        payload = await fetch_outlet_power_info(device_id)
        power_data = _normalize_single_outlet_power_payload(
            payload,
            requested_id=device_id,
        )
        if not power_data:
            return
        device = get_device_by_id(normalized_id)
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
