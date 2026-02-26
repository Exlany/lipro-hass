"""Schedule payload codec helpers for Lipro APIs."""

from __future__ import annotations

from collections.abc import Callable
import json
import logging
import re
from typing import Any

_LOGGER = logging.getLogger(__name__)
_HH_MM_TIME_PATTERN = re.compile(r"(\d{1,2}):(\d{2})")
_INVALID_JSON_PREVIEW_MAX_CHARS = 200


def coerce_int_list(value: Any) -> list[int]:
    """Convert mixed list payloads into a clean integer list."""
    if not isinstance(value, list):
        return []

    result: list[int] = []
    for item in value:
        if isinstance(item, bool):
            # Avoid treating bool as int.
            continue
        if isinstance(item, int):
            result.append(item)
            continue
        if isinstance(item, float):
            if item.is_integer():
                result.append(int(item))
            continue
        if isinstance(item, str):
            normalized = item.strip()
            if normalized.lstrip("+-").isdigit():
                try:
                    result.append(int(normalized))
                except ValueError:
                    continue
    return result


def parse_mesh_schedule_json(
    schedule_json: Any,
    *,
    coerce_connect_status: Callable[[Any], bool],
    mask_sensitive_data: Callable[[str], str],
) -> dict[str, list[int]]:
    """Parse mesh ``scheduleJson`` into normalized ``days/time/evt`` arrays."""
    empty: dict[str, list[int]] = {"days": [], "time": [], "evt": []}
    payload = schedule_json

    if isinstance(payload, str):
        raw = payload.strip()
        if not raw:
            return empty
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            _LOGGER.debug(
                "Invalid mesh scheduleJson payload (type=%s): %s",
                type(payload).__name__,
                mask_sensitive_data(str(payload)[:_INVALID_JSON_PREVIEW_MAX_CHARS]),
            )
            return empty

    if isinstance(payload, dict) and isinstance(payload.get("schedule"), dict):
        payload = payload["schedule"]

    if not isinstance(payload, dict):
        return empty

    days = coerce_int_list(payload.get("days"))
    times = coerce_int_list(payload.get("time"))
    events = coerce_int_list(payload.get("evt"))

    # Compatibility with richer scheduleJson variants from app docs.
    if not days:
        days = coerce_int_list(payload.get("weekDays"))

    if not times:
        hhmm = payload.get("time")
        if isinstance(hhmm, str):
            match = _HH_MM_TIME_PATTERN.fullmatch(hhmm.strip())
            if match:
                hours = int(match.group(1))
                minutes = int(match.group(2))
                if 0 <= hours <= 23 and 0 <= minutes <= 59:
                    times = [hours * 3600 + minutes * 60]

    if not events:
        action = payload.get("action")
        if (
            isinstance(action, dict)
            and str(action.get("command", "")).lower() == "power"
        ):
            props = action.get("properties")
            if isinstance(props, list):
                for prop in props:
                    if not isinstance(prop, dict):
                        continue
                    if prop.get("key") == "power":
                        events = [0 if coerce_connect_status(prop.get("value")) else 1]
                        break

    if len(times) != len(events):
        pair_count = min(len(times), len(events))
        if pair_count > 0:
            times = times[:pair_count]
            events = events[:pair_count]
        else:
            times = []
            events = []

    return {"days": days, "time": times, "evt": events}


def normalize_mesh_timing_rows(
    rows: list[Any],
    *,
    fallback_device_id: str = "",
    parse_schedule_json: Callable[[Any], dict[str, list[int]]],
    coerce_connect_status: Callable[[Any], bool],
) -> list[dict[str, Any]]:
    """Normalize mesh timing rows to include ``schedule`` dict payload."""
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue

        schedule_payload = row.get("schedule", row.get("scheduleJson"))
        schedule = parse_schedule_json(schedule_payload)

        normalized_row = dict(row)
        normalized_row["schedule"] = schedule
        normalized_row["active"] = coerce_connect_status(row.get("active", True))
        if not isinstance(normalized_row.get("deviceId"), str) and fallback_device_id:
            normalized_row["deviceId"] = fallback_device_id
        normalized_rows.append(normalized_row)

    return normalized_rows
