"""Internal REST decoder normalization helpers within the boundary family."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, Any, cast

from ...api.schedule_codec import parse_mesh_schedule_json
from ...api.types import DevicePropertyMap, JsonObject
from ...utils.identifiers import normalize_iot_device_id, normalize_mesh_group_id
from ...utils.property_normalization import normalize_properties

if TYPE_CHECKING:
    from ..contracts import (
        CanonicalDeviceListItem,
        CanonicalDeviceListPage,
        CanonicalDeviceStatusRow,
        CanonicalListEnvelope,
        CanonicalMeshGroupMember,
        CanonicalMeshGroupStatusRow,
        CanonicalMqttConfig,
        CanonicalScheduleJson,
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
    fallback_mapping: Mapping[str, Any] | None = None,
    excluded_keys: set[str] | None = None,
) -> DevicePropertyMap:
    if isinstance(payload, Mapping):
        return cast(DevicePropertyMap, normalize_properties(payload))
    if isinstance(payload, list):
        return _normalize_property_rows(payload)
    if fallback_mapping is None:
        return {}
    filtered = {
        key: value
        for key, value in fallback_mapping.items()
        if key not in (excluded_keys or set())
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


def _build_identity_aliases(row: Mapping[str, Any]) -> list[str]:
    aliases: list[str] = []
    seen: set[str] = set()
    for key in _DEVICE_ROW_ID_KEYS:
        normalized = _normalize_identifier(row.get(key))
        if normalized is None or normalized in seen:
            continue
        seen.add(normalized)
        aliases.append(normalized)
    return aliases


def _normalize_device_catalog_row(
    row: Mapping[str, Any],
) -> CanonicalDeviceListItem | None:
    identity_aliases = _build_identity_aliases(row)
    serial = next((alias for alias in identity_aliases if alias), None)
    if serial is None:
        return None

    device_number = row.get("deviceId")
    if isinstance(device_number, str):
        device_number = _normalize_identifier(device_number) or _normalize_string(device_number)
    if device_number is None:
        device_number = _normalize_identifier(row.get("id") or row.get("groupId")) or row.get("id", 0)

    properties = _normalize_properties_payload(row.get("properties"))
    canonical_data: dict[str, object] = {
        "deviceId": device_number,
        "serial": serial,
        "deviceName": _normalize_string(row.get("deviceName") or row.get("name"))
        or "Unknown",
        "type": row.get("type", row.get("deviceType", 1)),
        "iotName": _normalize_string(row.get("iotName")) or "",
        "isGroup": _coerce_bool(row.get("isGroup") or row.get("group"))
        or normalize_mesh_group_id(serial) is not None,
        "properties": properties,
        "identityAliases": identity_aliases,
    }
    for source_key, target_key in (
        ("roomId", "roomId"),
        ("roomName", "roomName"),
        ("productId", "productId"),
        ("physicalModel", "physicalModel"),
        ("model", "model"),
        ("online", "online"),
        ("category", "category"),
        ("homeId", "homeId"),
        ("homeName", "homeName"),
    ):
        if source_key in row:
            canonical_data[target_key] = row[source_key]
    return cast("CanonicalDeviceListItem", canonical_data)


def _extract_mqtt_config_mapping(
    result: object,
    *,
    is_success_code: Callable[[object], bool],
) -> CanonicalMqttConfig | None:
    """Extract the canonical MQTT-config mapping from known REST envelopes."""
    if not isinstance(result, dict):
        return None

    if "accessKey" in result and "secretKey" in result:
        return cast("CanonicalMqttConfig", dict(result))

    payload = result.get("data")
    if not isinstance(payload, dict):
        return None
    if "accessKey" not in payload or "secretKey" not in payload:
        return None
    if "code" not in result or is_success_code(result.get("code")):
        return cast("CanonicalMqttConfig", dict(payload))
    return None


def _decode_list_envelope_canonical(
    payload: object,
    *,
    offset: int = 0,
) -> CanonicalListEnvelope:
    rows = _extract_list_payload(payload)
    canonical: CanonicalListEnvelope = {
        "rows": rows,
        "has_more": False,
    }
    if not isinstance(payload, dict):
        return canonical

    if "hasMore" in payload:
        canonical["has_more"] = _coerce_bool(payload.get("hasMore"))
        return canonical

    total = _coerce_total(payload.get("total"))
    if total is None:
        return canonical

    canonical["total"] = total
    canonical["has_more"] = offset + len(rows) < total
    return canonical


def _extract_schedule_json_source(payload: object) -> object:
    if not isinstance(payload, Mapping):
        return payload
    if "scheduleJson" in payload:
        return payload.get("scheduleJson")
    if "payload" in payload:
        return payload.get("payload")
    return payload


def _decode_schedule_json_canonical(payload: object) -> CanonicalScheduleJson:
    parsed = parse_mesh_schedule_json(
        _extract_schedule_json_source(payload),
        mask_sensitive_data=lambda value: value,
    )
    return {
        "days": parsed["days"],
        "time": parsed["time"],
        "evt": parsed["evt"],
    }


def _build_schedule_json_fingerprint(payload: object) -> str:
    canonical = _decode_schedule_json_canonical(payload)
    return (
        f"days:{len(canonical['days'])}|"
        f"time:{len(canonical['time'])}|"
        f"evt:{len(canonical['evt'])}"
    )


def _decode_device_list_canonical(
    payload: object,
    *,
    offset: int = 0,
) -> CanonicalDeviceListPage:
    envelope = _decode_list_envelope_canonical(payload, offset=offset)
    rows_value = envelope.get("rows", [])
    rows = rows_value if isinstance(rows_value, list) else []
    devices = [
        canonical
        for row in rows
        if (canonical := _normalize_device_catalog_row(row)) is not None
    ]

    page_canonical: CanonicalDeviceListPage = {
        "devices": devices,
        "has_more": bool(envelope.get("has_more", False)),
    }
    total = envelope.get("total")
    if isinstance(total, int):
        page_canonical["total"] = total
    return page_canonical


def _decode_device_status_canonical(payload: object) -> list[CanonicalDeviceStatusRow]:
    envelope = _decode_list_envelope_canonical(payload)
    rows_value = envelope.get("rows", [])
    rows = rows_value if isinstance(rows_value, list) else []
    canonical_rows: list[CanonicalDeviceStatusRow] = []
    for row in rows:
        device_id = None
        for key in _STATUS_ROW_ID_KEYS:
            device_id = _normalize_identifier(row.get(key))
            if device_id is not None:
                break
        if device_id is None:
            continue

        properties = _normalize_properties_payload(
            row.get("properties"),
            fallback_mapping=row,
            excluded_keys=_STATUS_META_KEYS,
        )
        canonical_rows.append(
            {
                "deviceId": device_id,
                "properties": properties,
            }
        )
    return canonical_rows


def _decode_mesh_group_status_canonical(
    payload: object,
) -> list[CanonicalMeshGroupStatusRow]:
    envelope = _decode_list_envelope_canonical(payload)
    rows_value = envelope.get("rows", [])
    rows = rows_value if isinstance(rows_value, list) else []
    canonical_rows: list[CanonicalMeshGroupStatusRow] = []
    for row in rows:
        group_id = _normalize_identifier(row.get("groupId") or row.get("id"))
        if group_id is None:
            continue

        gateway_device_id = _normalize_identifier(row.get("gatewayDeviceId"))
        members: list[CanonicalMeshGroupMember] = []
        seen_member_ids: set[str] = set()
        raw_members = row.get("devices")
        if isinstance(raw_members, list):
            for member in raw_members:
                if not isinstance(member, Mapping):
                    continue
                member_id = _normalize_identifier(member.get("deviceId") or member.get("id"))
                if member_id is None or member_id in seen_member_ids:
                    continue
                seen_member_ids.add(member_id)
                members.append({"deviceId": member_id})

        properties = _normalize_properties_payload(
            row.get("properties"),
            fallback_mapping=row,
            excluded_keys=_STATUS_META_KEYS | {"gatewayDeviceId", "devices"},
        )
        canonical_rows.append(
            {
                "groupId": group_id,
                "gatewayDeviceId": gateway_device_id,
                "devices": members,
                "properties": properties,
            }
        )
    return canonical_rows


__all__ = [
    "_build_payload_fingerprint",
    "_build_schedule_json_fingerprint",
    "_decode_device_list_canonical",
    "_decode_device_status_canonical",
    "_decode_list_envelope_canonical",
    "_decode_mesh_group_status_canonical",
    "_decode_schedule_json_canonical",
    "_extract_mqtt_config_mapping",
]
