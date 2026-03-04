"""Schedule endpoint payload helpers for Lipro APIs."""

from __future__ import annotations

from collections.abc import Callable
import json
from typing import Any

from ..utils.identifiers import is_mesh_group_id_prefix


def is_mesh_group_id(device_id: str) -> bool:
    """Return whether an identifier is a mesh-group ID."""
    return is_mesh_group_id_prefix(device_id)


def resolve_mesh_schedule_candidate_ids(
    device_id: str,
    *,
    mesh_gateway_id: str = "",
    mesh_member_ids: list[str] | None = None,
    normalize_iot_device_id: Callable[[Any], str | None],
) -> list[str]:
    """Resolve candidate IoT IDs for mesh schedule APIs."""
    candidates: list[str] = []
    seen: set[str] = set()

    def _append_candidate(raw_id: Any) -> None:
        normalized = normalize_iot_device_id(raw_id)
        if normalized is None or normalized in seen:
            return
        seen.add(normalized)
        candidates.append(normalized)

    _append_candidate(mesh_gateway_id)
    if isinstance(mesh_member_ids, list):
        for member_id in mesh_member_ids:
            _append_candidate(member_id)
    _append_candidate(device_id)
    return candidates


def encode_mesh_schedule_json(
    days: list[int],
    times: list[int],
    events: list[int],
) -> str:
    """Encode mesh schedule payload as compact JSON."""
    return json.dumps(
        {"days": days, "time": times, "evt": events},
        separators=(",", ":"),
        ensure_ascii=False,
    )


def build_mesh_schedule_get_body(device_id: str) -> dict[str, Any]:
    """Build BLE mesh schedule GET request body."""
    return {
        "deviceId": device_id,
        "deviceType": "mesh",
    }


def build_mesh_schedule_add_body(
    device_id: str,
    *,
    schedule_json: str,
) -> dict[str, Any]:
    """Build BLE mesh schedule ADD request body."""
    return {
        "deviceId": device_id,
        "id": 0,
        "scheduleJson": schedule_json,
        "active": True,
    }


def build_mesh_schedule_delete_body(
    device_id: str,
    *,
    schedule_ids: list[int],
) -> dict[str, Any]:
    """Build BLE mesh schedule DELETE request body."""
    return {
        "deviceId": device_id,
        "idList": schedule_ids,
    }


def build_schedule_get_body(
    device_id: str,
    *,
    device_type_hex: str,
) -> dict[str, Any]:
    """Build standard schedule GET request body."""
    return {
        "deviceId": device_id,
        "deviceType": device_type_hex,
    }


def build_schedule_add_body(
    device_id: str,
    *,
    device_type_hex: str,
    days: list[int],
    times: list[int],
    events: list[int],
    group_id: str,
) -> dict[str, Any]:
    """Build standard schedule ADD request body."""
    return {
        "deviceId": device_id,
        "deviceType": device_type_hex,
        "scheduleInfo": {
            "days": days,
            "time": times,
            "evt": events,
        },
        "groupId": group_id,
        "singleBle": False,
    }


def build_schedule_delete_body(
    device_id: str,
    *,
    device_type_hex: str,
    schedule_ids: list[int],
    group_id: str,
) -> dict[str, Any]:
    """Build standard schedule DELETE request body."""
    return {
        "deviceId": device_id,
        "deviceType": device_type_hex,
        "idList": schedule_ids,
        "groupId": group_id,
        "singleBle": False,
    }
