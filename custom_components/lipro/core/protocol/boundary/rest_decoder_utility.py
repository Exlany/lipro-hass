"""Utility helpers shared by REST boundary decoder collaborators."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, cast

from ...api.types import DevicePropertyMap, JsonObject
from ...utils.identifiers import normalize_iot_device_id, normalize_mesh_group_id
from ...utils.property_normalization import normalize_properties

if TYPE_CHECKING:
    from ..contracts import (
        CanonicalDeviceListItem,
        CanonicalMeshGroupMember,
    )

_DEVICE_ROW_ID_KEYS = (
    "serial",
    "iotDeviceId",
    "iotId",
    "groupId",
    "id",
    "deviceId",
)
_STATUS_ROW_ID_KEYS = (
    "iotId",
    "groupId",
    "deviceId",
    "id",
)
_STATUS_META_KEYS = {
    *_STATUS_ROW_ID_KEYS,
    "code",
    "msg",
    "message",
    "success",
    "data",
}
_CATALOG_OPTIONAL_FIELDS = (
    ("roomId", "roomId"),
    ("roomName", "roomName"),
    ("productId", "productId"),
    ("physicalModel", "physicalModel"),
    ("model", "model"),
    ("online", "online"),
    ("category", "category"),
    ("homeId", "homeId"),
    ("homeName", "homeName"),
)
_FALLBACK_PROPERTY_EXCLUDED_KEYS = {
    "category",
    "data",
    "deviceName",
    "deviceType",
    "devices",
    "gatewayDeviceId",
    "group",
    "iotName",
    "model",
    "name",
    "online",
    "payload",
    "physicalModel",
    "properties",
    "roomId",
    "roomName",
    "serial",
    "type",
}
_FALLBACK_PROPERTY_EXCLUDED_SUFFIXES = ("Id", "Name", "Model")
type ShouldIncludeFallbackProperty = Callable[..., bool]


def _normalize_pagination_offset(offset: int) -> int:
    return max(0, offset)


def _is_scalar_property_value(value: object) -> bool:
    return not isinstance(value, Mapping | list | tuple | set)


def _should_include_fallback_property(
    key: object,
    value: object,
    *,
    excluded_keys: set[str],
) -> bool:
    if not isinstance(key, str) or not key:
        return False
    if key in excluded_keys or key in _FALLBACK_PROPERTY_EXCLUDED_KEYS:
        return False
    if key.endswith(_FALLBACK_PROPERTY_EXCLUDED_SUFFIXES):
        return False
    return _is_scalar_property_value(value)


def _build_payload_fingerprint(payload: object) -> str:
    """Return a shape-only fingerprint safe for telemetry and replay tags."""
    if isinstance(payload, list):
        if not payload:
            return "list[empty]"
        first = payload[0]
        if isinstance(first, dict):
            keys = ",".join(sorted(str(key) for key in first))
            return f"list[dict[{keys}]]"
        return f"list[{type(first).__name__}]"
    if not isinstance(payload, dict):
        return type(payload).__name__
    top_keys = ",".join(sorted(str(key) for key in payload))
    for nested_key in ("data", "devices"):
        nested = payload.get(nested_key)
        if isinstance(nested, dict):
            nested_keys = ",".join(sorted(str(key) for key in nested))
            return f"dict[{top_keys}]::{nested_key}[{nested_keys}]"
        if isinstance(nested, list):
            if not nested:
                return f"dict[{top_keys}]::{nested_key}[empty-list]"
            first = nested[0]
            if isinstance(first, dict):
                nested_keys = ",".join(sorted(str(key) for key in first))
                return f"dict[{top_keys}]::{nested_key}[dict[{nested_keys}]]"
            return f"dict[{top_keys}]::{nested_key}[{type(first).__name__}]"
    return f"dict[{top_keys}]"


def _normalize_string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return normalized


def _normalize_identifier(value: object) -> str | None:
    normalized = normalize_iot_device_id(value)
    if normalized is not None:
        return normalized
    normalized = normalize_mesh_group_id(value)
    if normalized is not None:
        return normalized
    return _normalize_string(value)


def _coerce_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        return normalized in {"1", "true", "yes", "on"}
    return False


def _normalize_property_rows(rows: Sequence[object]) -> DevicePropertyMap:
    normalized: DevicePropertyMap = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        key = row.get("key")
        if isinstance(key, str) and key:
            normalized[key] = row.get("value")
    return cast(DevicePropertyMap, normalize_properties(normalized))


def _normalize_properties_payload(
    payload: object,
    *,
    fallback_mapping: Mapping[str, object] | None = None,
    excluded_keys: set[str] | None = None,
    should_include_fallback_property: ShouldIncludeFallbackProperty = _should_include_fallback_property,
) -> DevicePropertyMap:
    if isinstance(payload, Mapping):
        return cast(DevicePropertyMap, normalize_properties(payload))
    if isinstance(payload, list):
        return _normalize_property_rows(payload)
    if fallback_mapping is None:
        return {}
    resolved_excluded_keys = excluded_keys or set()
    filtered = {
        key: value
        for key, value in fallback_mapping.items()
        if should_include_fallback_property(
            key,
            value,
            excluded_keys=resolved_excluded_keys,
        )
    }
    return cast(DevicePropertyMap, normalize_properties(filtered))


def _extract_list_payload(result: object) -> list[JsonObject]:
    if isinstance(result, list):
        return [cast(JsonObject, dict(row)) for row in result if isinstance(row, dict)]
    if isinstance(result, dict):
        for key in ("devices", "data"):
            value = result.get(key)
            if isinstance(value, list):
                return [
                    cast(JsonObject, dict(row)) for row in value if isinstance(row, dict)
                ]
    return []


def _coerce_total(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        normalized = value.strip()
        if normalized.isdecimal():
            return int(normalized)
    return None


def _build_identity_aliases(row: Mapping[str, object]) -> list[str]:
    aliases: list[str] = []
    seen: set[str] = set()
    for key in _DEVICE_ROW_ID_KEYS:
        normalized = _normalize_identifier(row.get(key))
        if normalized is None or normalized in seen:
            continue
        seen.add(normalized)
        aliases.append(normalized)
    return aliases


def _resolve_device_catalog_number(row: Mapping[str, object]) -> object:
    device_number: object = row.get("deviceId")
    if isinstance(device_number, str):
        return _normalize_identifier(device_number) or _normalize_string(device_number)
    if device_number is None:
        return _normalize_identifier(row.get("id") or row.get("groupId")) or row.get(
            "id", 0
        )
    return device_number


def _copy_catalog_optional_fields(
    row: Mapping[str, object],
    *,
    target: dict[str, object],
) -> None:
    for source_key, target_key in _CATALOG_OPTIONAL_FIELDS:
        if source_key in row:
            target[target_key] = row[source_key]


def _extract_status_identifier(row: Mapping[str, object]) -> str | None:
    for key in _STATUS_ROW_ID_KEYS:
        device_id = _normalize_identifier(row.get(key))
        if device_id is not None:
            return device_id
    return None


def _normalize_mesh_group_members(
    raw_members: object,
) -> list[CanonicalMeshGroupMember]:
    members: list[CanonicalMeshGroupMember] = []
    seen_member_ids: set[str] = set()
    if not isinstance(raw_members, list):
        return members
    for member in raw_members:
        if not isinstance(member, Mapping):
            continue
        member_id = _normalize_identifier(member.get("deviceId") or member.get("id"))
        if member_id is None or member_id in seen_member_ids:
            continue
        seen_member_ids.add(member_id)
        members.append({"deviceId": member_id})
    return members


def _normalize_device_catalog_row(
    row: Mapping[str, object],
) -> CanonicalDeviceListItem | None:
    identity_aliases = _build_identity_aliases(row)
    serial = next((alias for alias in identity_aliases if alias), None)
    if serial is None:
        return None

    canonical_data: dict[str, object] = {
        "deviceId": _resolve_device_catalog_number(row),
        "serial": serial,
        "deviceName": _normalize_string(row.get("deviceName") or row.get("name"))
        or "Unknown",
        "type": row.get("type", row.get("deviceType", 1)),
        "iotName": _normalize_string(row.get("iotName")) or "",
        "isGroup": _coerce_bool(row.get("isGroup") or row.get("group"))
        or normalize_mesh_group_id(serial) is not None,
        "properties": _normalize_properties_payload(row.get("properties")),
        "identityAliases": identity_aliases,
    }
    _copy_catalog_optional_fields(row, target=canonical_data)
    return cast("CanonicalDeviceListItem", canonical_data)


__all__ = [
    "_FALLBACK_PROPERTY_EXCLUDED_KEYS",
    "_FALLBACK_PROPERTY_EXCLUDED_SUFFIXES",
    "_STATUS_META_KEYS",
    "_build_payload_fingerprint",
    "_coerce_bool",
    "_coerce_total",
    "_extract_list_payload",
    "_extract_status_identifier",
    "_normalize_device_catalog_row",
    "_normalize_identifier",
    "_normalize_mesh_group_members",
    "_normalize_pagination_offset",
    "_normalize_properties_payload",
    "_should_include_fallback_property",
]
