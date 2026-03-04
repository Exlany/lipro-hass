"""Pure decision helpers for mesh group lookup-id mappings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class GroupLookupMappingDecision:
    """Computed changes needed to apply mesh group lookup-id mappings."""

    gateway_unregister_id: str | None
    gateway_register_id: str | None
    gateway_extra_data_value: str | None
    member_unregister_ids: list[str]
    member_register_ids: list[str]
    member_lookup_ids_extra_data: list[str]
    member_ids_extra_data: list[str]
    member_count: int


def _normalize_lookup_id(value: str) -> str:
    return value.strip().lower()


def index_lookup_ids_by_normalized(lookup_ids: list[Any] | Any) -> dict[str, str]:
    """Index lookup IDs by normalized key while preserving first-seen value."""
    if not isinstance(lookup_ids, list):
        return {}
    indexed: dict[str, str] = {}
    for lookup_id in lookup_ids:
        if not isinstance(lookup_id, str):
            continue
        stripped = lookup_id.strip()
        if not stripped:
            continue
        indexed.setdefault(stripped.lower(), stripped)
    return indexed


def compute_group_lookup_mapping_decision(
    *,
    previous_gateway_id: Any,
    current_gateway_id: Any,
    previous_member_lookup_ids: Any,
    current_member_lookup_ids: Any,
    member_ids: list[str],
) -> GroupLookupMappingDecision:
    """Compute lookup-id register/unregister actions and extra_data updates."""
    gateway_unregister_id: str | None = None
    if (
        isinstance(previous_gateway_id, str)
        and previous_gateway_id.strip()
        and (
            not isinstance(current_gateway_id, str)
            or _normalize_lookup_id(previous_gateway_id)
            != _normalize_lookup_id(current_gateway_id)
        )
    ):
        gateway_unregister_id = previous_gateway_id

    gateway_register_id = (
        current_gateway_id if isinstance(current_gateway_id, str) else None
    )
    gateway_extra_data_value = (
        gateway_register_id.strip()
        if gateway_register_id and gateway_register_id.strip()
        else None
    )

    previous_indexed = index_lookup_ids_by_normalized(previous_member_lookup_ids)
    current_indexed = index_lookup_ids_by_normalized(current_member_lookup_ids)
    stale_norms = set(previous_indexed) - set(current_indexed)
    member_unregister_ids = [previous_indexed[norm] for norm in stale_norms]

    member_register_ids = list(current_indexed.values())
    member_lookup_ids_extra_data = list(current_indexed.values())

    return GroupLookupMappingDecision(
        gateway_unregister_id=gateway_unregister_id,
        gateway_register_id=gateway_extra_data_value,
        gateway_extra_data_value=gateway_extra_data_value,
        member_unregister_ids=member_unregister_ids,
        member_register_ids=member_register_ids,
        member_lookup_ids_extra_data=member_lookup_ids_extra_data,
        member_ids_extra_data=member_ids,
        member_count=len(member_ids),
    )
