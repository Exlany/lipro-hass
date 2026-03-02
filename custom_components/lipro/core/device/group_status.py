"""Mesh-group status parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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
