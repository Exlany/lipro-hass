"""Runtime helpers for outlet power querying."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import logging
import math
from typing import Any

from ...api import LiproApiError

_POWER_BATCH_LIST_KEYS: tuple[str, ...] = (
    "data",
    "result",
    "devices",
    "list",
)


def _normalize_device_id(value: Any) -> str | None:
    """Normalize a device identifier for case/whitespace tolerant matching."""
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return normalized.lower()


def _extract_power_rows(payload: Any) -> list[dict[str, Any]] | None:
    """Extract list payload variants from batch power-info responses."""
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        containers: list[dict[str, Any]] = [payload]
        for _ in range(3):
            nested: list[dict[str, Any]] = []
            for container in containers:
                for key in _POWER_BATCH_LIST_KEYS:
                    value = container.get(key)
                    if isinstance(value, list):
                        return [row for row in value if isinstance(row, dict)]
                    if isinstance(value, dict):
                        nested.append(value)
            if not nested:
                break
            containers = nested
    return None


def _normalize_outlet_power_payload(
    payload: Any,
    *,
    requested_ids: list[str],
) -> dict[str, dict[str, Any]] | None:
    """Normalize outlet power payload into a per-device mapping.

    The Lipro API may return several shapes:
    - Single-device mapping (no ``deviceId`` field): ``{"nowPower": ...}``
    - Batch mapping keyed by device ID: ``{"<deviceId>": {...}, ...}``
    - Batch list rows (direct or nested under keys like ``data``): ``[{...}, ...]``
    """
    normalized_requested = {
        normalized_id
        for raw_id in requested_ids
        if (normalized_id := _normalize_device_id(raw_id)) is not None
    }
    if not normalized_requested:
        return {}

    if isinstance(payload, dict):
        by_device_id: dict[str, dict[str, Any]] = {}
        for key, value in payload.items():
            normalized_key = _normalize_device_id(key)
            if normalized_key is None or normalized_key not in normalized_requested:
                continue
            if isinstance(value, dict):
                by_device_id[normalized_key] = value

        if by_device_id:
            return by_device_id

        rows = _extract_power_rows(payload)
        if rows is not None:
            return _normalize_outlet_power_payload(rows, requested_ids=requested_ids)

        for key in _POWER_BATCH_LIST_KEYS:
            nested = payload.get(key)
            if isinstance(nested, dict):
                normalized_payload = _normalize_outlet_power_payload(
                    nested,
                    requested_ids=requested_ids,
                )
                if normalized_payload is not None:
                    return normalized_payload

        if len(normalized_requested) == 1 and payload:
            # Single-device payload without a deviceId field.
            device_id = next(iter(normalized_requested))
            return {device_id: payload}

        return None

    rows = _extract_power_rows(payload)
    if rows is None:
        return None

    by_device_id_rows: dict[str, dict[str, Any]] = {}
    for row in rows:
        normalized_id = _normalize_device_id(row.get("deviceId"))
        if normalized_id is None or normalized_id not in normalized_requested:
            continue
        by_device_id_rows[normalized_id] = row

    return by_device_id_rows or None


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
    fetch_outlet_power_info: Callable[[list[str]], Awaitable[Any]],
    get_device_by_id: Callable[[Any], Any],
    apply_outlet_power_info: Callable[[Any, dict[str, Any]], bool],
    should_reraise_outlet_power_error: Callable[[LiproApiError], bool],
    logger: logging.Logger,
    concurrency: int,
) -> int:
    """Query outlet power info in bounded concurrent slices.

    Returns the updated round-robin index to persist in the coordinator.
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

    if len(outlet_ids) == 1:
        await _query_single(outlet_ids[0])
        return updated_index

    try:
        payload = await fetch_outlet_power_info(outlet_ids)
        normalized = _normalize_outlet_power_payload(
            payload,
            requested_ids=outlet_ids,
        )
        if normalized:
            for device_id, power_data in normalized.items():
                device = get_device_by_id(device_id)
                if device is not None and apply_outlet_power_info(device, power_data):
                    logger.debug(
                        "Updated power info for %s: nowPower=%s",
                        device.name,
                        power_data.get("nowPower"),
                    )
            return updated_index
        logger.debug(
            "Power-info batch payload could not be normalized (devices=%d), falling back",
            len(outlet_ids),
        )
    except LiproApiError as err:
        if should_reraise_outlet_power_error(err):
            raise
        logger.debug(
            "Failed to query power batch (devices=%d): %s",
            len(outlet_ids),
            err,
        )

    batch_size = min(concurrency, len(outlet_ids))
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
    fetch_outlet_power_info: Callable[[list[str]], Awaitable[Any]],
    get_device_by_id: Callable[[Any], Any],
    apply_outlet_power_info: Callable[[Any, dict[str, Any]], bool],
    should_reraise_outlet_power_error: Callable[[LiproApiError], bool],
    logger: logging.Logger,
) -> None:
    """Query and apply power info for one outlet device."""
    normalized_id = _normalize_device_id(device_id)
    if normalized_id is None:
        return

    try:
        payload = await fetch_outlet_power_info([device_id])
        normalized = _normalize_outlet_power_payload(
            payload,
            requested_ids=[device_id],
        )
        power_data = normalized.get(normalized_id) if normalized else None
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
