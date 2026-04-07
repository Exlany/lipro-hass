"""Mesh-group status parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..utils.identifiers import normalize_iot_device_id

if TYPE_CHECKING:
    from .device import LiproDevice


@dataclass(frozen=True)
class MeshGroupLookupIds:
    """Lookup identifiers resolved from one mesh-group status payload."""

    gateway_id: Any
    member_lookup_ids: list[Any]
    member_ids: list[str]


def resolve_mesh_group_lookup_ids(status_data: dict[str, Any]) -> MeshGroupLookupIds:
    """Resolve gateway/member IDs from group status payload."""
    gateway_id = status_data.get("gatewayDeviceId")
    member_lookup_ids: list[Any] = []
    member_ids: list[str] = []

    members = status_data.get("devices")
    if isinstance(members, list):
        for member in members:
            if not isinstance(member, dict):
                continue
            member_id = member.get("deviceId")
            member_lookup_ids.append(member_id)
            if isinstance(member_id, str) and member_id.strip():
                member_ids.append(member_id.strip())

    return MeshGroupLookupIds(
        gateway_id=gateway_id,
        member_lookup_ids=member_lookup_ids,
        member_ids=member_ids,
    )


def sync_mesh_group_extra_data(
    device: LiproDevice,
    status_data: dict[str, Any],
) -> bool:
    """Synchronize mesh-group metadata into ``device.extra_data``.

    The mesh-group status endpoint is the authoritative source for:
    - ``gatewayDeviceId`` → ``extra_data["gateway_device_id"]``
    - ``devices[].deviceId`` → ``extra_data["group_member_ids"]``

    Missing keys are treated as "no update" so partial payloads do not clear
    previously learned metadata.
    """
    if not device.is_group:
        return False

    resolved = resolve_mesh_group_lookup_ids(status_data)
    changed = False

    if "gatewayDeviceId" in status_data:
        gateway_id = normalize_iot_device_id(resolved.gateway_id)
        if gateway_id is None:
            if device.extra_data.pop("gateway_device_id", None) is not None:
                changed = True
        elif device.extra_data.get("gateway_device_id") != gateway_id:
            device.extra_data["gateway_device_id"] = gateway_id
            changed = True

    if isinstance(status_data.get("devices"), list):
        member_ids: list[str] = []
        seen: set[str] = set()
        for member_id in resolved.member_ids:
            normalized = normalize_iot_device_id(member_id)
            if normalized is None or normalized in seen:
                continue
            seen.add(normalized)
            member_ids.append(normalized)

        if member_ids:
            if device.extra_data.get("group_member_ids") != member_ids:
                device.extra_data["group_member_ids"] = member_ids
                changed = True
        elif device.extra_data.pop("group_member_ids", None) is not None:
            changed = True

    return changed
