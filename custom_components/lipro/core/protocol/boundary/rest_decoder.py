"""REST-side decoder contracts and concrete family implementations."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

from ...utils.identifiers import normalize_iot_device_id, normalize_mesh_group_id
from ...utils.property_normalization import normalize_properties
from .result import BoundaryDecodeResult, BoundaryDecoderKey

CanonicalT = TypeVar("CanonicalT")
_REST_MQTT_CONFIG_FAMILY = "rest.mqtt-config"
_REST_MQTT_CONFIG_VERSION = "v1"
_REST_MQTT_CONFIG_AUTHORITY = "tests/fixtures/api_contracts/get_mqtt_config.*.json"
_REST_DEVICE_LIST_FAMILY = "rest.device-list"
_REST_DEVICE_LIST_VERSION = "v1"
_REST_DEVICE_LIST_AUTHORITY = "tests/fixtures/api_contracts/get_device_list.*.json"
_REST_DEVICE_STATUS_FAMILY = "rest.device-status"
_REST_DEVICE_STATUS_VERSION = "v1"
_REST_DEVICE_STATUS_AUTHORITY = "tests/fixtures/api_contracts/query_device_status.*.json"
_REST_MESH_GROUP_STATUS_FAMILY = "rest.mesh-group-status"
_REST_MESH_GROUP_STATUS_VERSION = "v1"
_REST_MESH_GROUP_STATUS_AUTHORITY = (
    "tests/fixtures/api_contracts/query_mesh_group_status.*.json"
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
_DEVICE_LIST_META_KEYS = {
    "total",
    "hasMore",
    "devices",
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


def _normalize_property_rows(rows: Sequence[object]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        key = row.get("key")
        if isinstance(key, str) and key:
            normalized[key] = row.get("value")
    return normalize_properties(normalized)


def _normalize_properties_payload(
    payload: object,
    *,
    fallback_mapping: Mapping[str, Any] | None = None,
    excluded_keys: set[str] | None = None,
) -> dict[str, Any]:
    if isinstance(payload, Mapping):
        return normalize_properties(payload)
    if isinstance(payload, list):
        return _normalize_property_rows(payload)
    if fallback_mapping is None:
        return {}
    filtered = {
        key: value
        for key, value in fallback_mapping.items()
        if key not in (excluded_keys or set())
    }
    return normalize_properties(filtered)


def _extract_list_payload(result: object) -> list[dict[str, Any]]:
    if isinstance(result, list):
        return [dict(row) for row in result if isinstance(row, dict)]
    if isinstance(result, dict):
        for key in ("devices", "data"):
            value = result.get(key)
            if isinstance(value, list):
                return [dict(row) for row in value if isinstance(row, dict)]
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


def _normalize_device_catalog_row(row: Mapping[str, Any]) -> dict[str, Any] | None:
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
    canonical = {
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
            canonical[target_key] = row[source_key]
    return canonical


def _extract_mqtt_config_mapping(
    result: object,
    *,
    is_success_code: Callable[[object], bool],
) -> dict[str, Any] | None:
    """Extract the canonical MQTT-config mapping from known REST envelopes."""
    if not isinstance(result, dict):
        return None

    if "accessKey" in result and "secretKey" in result:
        return dict(result)

    payload = result.get("data")
    if not isinstance(payload, dict):
        return None
    if "accessKey" not in payload or "secretKey" not in payload:
        return None
    if "code" not in result or is_success_code(result.get("code")):
        return dict(payload)
    return None


def _decode_device_list_canonical(
    payload: object,
    *,
    offset: int = 0,
) -> dict[str, Any]:
    rows = _extract_list_payload(payload)
    devices = [
        canonical
        for row in rows
        if (canonical := _normalize_device_catalog_row(row)) is not None
    ]

    has_more = False
    total = None
    if isinstance(payload, dict):
        if "hasMore" in payload:
            has_more = _coerce_bool(payload.get("hasMore"))
        else:
            total = _coerce_total(payload.get("total"))
            if total is not None:
                has_more = offset + len(devices) < total

    canonical: dict[str, Any] = {
        "devices": devices,
        "has_more": has_more,
    }
    if total is not None:
        canonical["total"] = total
    return canonical


def _decode_device_status_canonical(payload: object) -> list[dict[str, Any]]:
    rows = _extract_list_payload(payload)
    canonical_rows: list[dict[str, Any]] = []
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


def _decode_mesh_group_status_canonical(payload: object) -> list[dict[str, Any]]:
    rows = _extract_list_payload(payload)
    canonical_rows: list[dict[str, Any]] = []
    for row in rows:
        group_id = _normalize_identifier(row.get("groupId") or row.get("id"))
        if group_id is None:
            continue

        gateway_device_id = _normalize_identifier(row.get("gatewayDeviceId"))
        members: list[dict[str, str]] = []
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


@dataclass(frozen=True, slots=True)
class RestDecodeContext:
    """Describe one REST decoder family's endpoint-scoped authority."""

    family: str
    endpoint: str
    authority: str
    version: str = "v1"

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the stable family/version identity for registry use."""
        return BoundaryDecoderKey(family=self.family, version=self.version)


class RestBoundaryDecoder(Protocol[CanonicalT]):
    """Protocol for one REST payload decoder family."""

    @property
    def context(self) -> RestDecodeContext:
        """Return endpoint-bound decoder metadata."""
        ...

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the registry key for this family implementation."""
        ...

    @property
    def authority(self) -> str:
        """Return the authoritative source backing this decoder family."""
        ...

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalT]:
        """Decode one REST payload to a canonical protocol contract."""
        ...


class MqttConfigRestDecoder:
    """Decode the MQTT-config REST family into the canonical contract shape."""

    def __init__(self, *, is_success_code: Callable[[object], bool]) -> None:
        """Store the success-code predicate used by the vendor REST envelope."""
        self._is_success_code = is_success_code
        self._context = RestDecodeContext(
            family=_REST_MQTT_CONFIG_FAMILY,
            endpoint="get_mqtt_config",
            authority=_REST_MQTT_CONFIG_AUTHORITY,
            version=_REST_MQTT_CONFIG_VERSION,
        )

    @property
    def context(self) -> RestDecodeContext:
        """Return the metadata describing this decoder family."""
        return self._context

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the family/version identity used by the registry."""
        return self._context.key

    @property
    def authority(self) -> str:
        """Return the authoritative source backing this family."""
        return self._context.authority

    def decode(self, payload: object) -> BoundaryDecodeResult[dict[str, Any]]:
        """Decode the MQTT-config response into a canonical mapping."""
        canonical = _extract_mqtt_config_mapping(
            payload,
            is_success_code=self._is_success_code,
        )
        if canonical is None:
            message = "MQTT config response missing accessKey/secretKey"
            raise ValueError(message)
        return BoundaryDecodeResult(
            key=self.key,
            canonical=canonical,
            authority=self.authority,
            fingerprint=_build_payload_fingerprint(payload),
        )


class DeviceListRestDecoder:
    """Decode device-list payloads into a canonical catalog page contract."""

    def __init__(self, *, offset: int = 0) -> None:
        """Bind the decoder to one pagination offset for `has_more` calculation."""
        self._offset = max(0, offset)
        self._context = RestDecodeContext(
            family=_REST_DEVICE_LIST_FAMILY,
            endpoint="get_device_list",
            authority=_REST_DEVICE_LIST_AUTHORITY,
            version=_REST_DEVICE_LIST_VERSION,
        )

    @property
    def context(self) -> RestDecodeContext:
        """Return the metadata describing this decoder family."""
        return self._context

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the family/version identity used by the registry."""
        return self._context.key

    @property
    def authority(self) -> str:
        """Return the authoritative fixture source backing this family."""
        return self._context.authority

    def decode(self, payload: object) -> BoundaryDecodeResult[dict[str, Any]]:
        """Decode one device-list payload into the canonical catalog page."""
        canonical = _decode_device_list_canonical(payload, offset=self._offset)
        return BoundaryDecodeResult(
            key=self.key,
            canonical=canonical,
            authority=self.authority,
            fingerprint=_build_payload_fingerprint(payload),
        )


class DeviceStatusRestDecoder:
    """Decode device-status payloads into canonical status rows."""

    def __init__(self) -> None:
        """Initialize one device-status decoder bound to its authority family."""
        self._context = RestDecodeContext(
            family=_REST_DEVICE_STATUS_FAMILY,
            endpoint="query_device_status",
            authority=_REST_DEVICE_STATUS_AUTHORITY,
            version=_REST_DEVICE_STATUS_VERSION,
        )

    @property
    def context(self) -> RestDecodeContext:
        """Return the metadata describing this decoder family."""
        return self._context

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the family/version identity used by the registry."""
        return self._context.key

    @property
    def authority(self) -> str:
        """Return the authoritative fixture source backing this family."""
        return self._context.authority

    def decode(self, payload: object) -> BoundaryDecodeResult[list[dict[str, Any]]]:
        """Decode one device-status payload into canonical rows."""
        return BoundaryDecodeResult(
            key=self.key,
            canonical=_decode_device_status_canonical(payload),
            authority=self.authority,
            fingerprint=_build_payload_fingerprint(payload),
        )


class MeshGroupStatusRestDecoder:
    """Decode mesh-group-status payloads into canonical topology rows."""

    def __init__(self) -> None:
        """Initialize one device-status decoder bound to its authority family."""
        self._context = RestDecodeContext(
            family=_REST_MESH_GROUP_STATUS_FAMILY,
            endpoint="query_mesh_group_status",
            authority=_REST_MESH_GROUP_STATUS_AUTHORITY,
            version=_REST_MESH_GROUP_STATUS_VERSION,
        )

    @property
    def context(self) -> RestDecodeContext:
        """Return the metadata describing this decoder family."""
        return self._context

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the family/version identity used by the registry."""
        return self._context.key

    @property
    def authority(self) -> str:
        """Return the authoritative fixture source backing this family."""
        return self._context.authority

    def decode(self, payload: object) -> BoundaryDecodeResult[list[dict[str, Any]]]:
        """Decode one mesh-group-status payload into canonical topology rows."""
        return BoundaryDecodeResult(
            key=self.key,
            canonical=_decode_mesh_group_status_canonical(payload),
            authority=self.authority,
            fingerprint=_build_payload_fingerprint(payload),
        )


def decode_mqtt_config_payload(
    payload: object,
    *,
    is_success_code: Callable[[object], bool],
) -> BoundaryDecodeResult[dict[str, Any]]:
    """Decode one MQTT-config REST payload through the formal boundary family."""
    return MqttConfigRestDecoder(is_success_code=is_success_code).decode(payload)


def decode_device_list_payload(
    payload: object,
    *,
    offset: int = 0,
) -> BoundaryDecodeResult[dict[str, Any]]:
    """Decode one device-list REST payload into the canonical catalog page."""
    return DeviceListRestDecoder(offset=offset).decode(payload)


def decode_device_status_payload(
    payload: object,
) -> BoundaryDecodeResult[list[dict[str, Any]]]:
    """Decode one device-status REST payload into canonical status rows."""
    return DeviceStatusRestDecoder().decode(payload)


def decode_mesh_group_status_payload(
    payload: object,
) -> BoundaryDecodeResult[list[dict[str, Any]]]:
    """Decode one mesh-group-status REST payload into canonical topology rows."""
    return MeshGroupStatusRestDecoder().decode(payload)
