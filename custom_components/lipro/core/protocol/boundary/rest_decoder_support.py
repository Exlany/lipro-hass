"""Internal REST decoder normalization helpers within the boundary family."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .rest_decoder_utility import (
    _FALLBACK_PROPERTY_EXCLUDED_KEYS as _FALLBACK_PROPERTY_EXCLUDED_KEYS_IMPL,
    _FALLBACK_PROPERTY_EXCLUDED_SUFFIXES as _FALLBACK_PROPERTY_EXCLUDED_SUFFIXES_IMPL,
    _STATUS_META_KEYS,
    _coerce_bool,
    _coerce_total,
    _extract_list_payload,
    _extract_status_identifier,
    _normalize_device_catalog_row,
    _normalize_identifier,
    _normalize_mesh_group_members,
    _normalize_pagination_offset as _normalize_pagination_offset_impl,
    _normalize_properties_payload,
    _should_include_fallback_property as _should_include_fallback_property_impl,
)

if TYPE_CHECKING:
    from ..contracts import (
        CanonicalDeviceListPage,
        CanonicalDeviceStatusRow,
        CanonicalListEnvelope,
        CanonicalMeshGroupStatusRow,
    )

_FALLBACK_PROPERTY_EXCLUDED_KEYS = _FALLBACK_PROPERTY_EXCLUDED_KEYS_IMPL
_FALLBACK_PROPERTY_EXCLUDED_SUFFIXES = _FALLBACK_PROPERTY_EXCLUDED_SUFFIXES_IMPL


def _normalize_pagination_offset(offset: int) -> int:
    return _normalize_pagination_offset_impl(offset)


def _should_include_fallback_property(
    key: object,
    value: object,
    *,
    excluded_keys: set[str],
) -> bool:
    return _should_include_fallback_property_impl(
        key,
        value,
        excluded_keys=excluded_keys,
    )


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
    canonical["has_more"] = _normalize_pagination_offset(offset) + len(rows) < total
    return canonical


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
        device_id = _extract_status_identifier(row)
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
        members = _normalize_mesh_group_members(row.get("devices"))

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
    "_decode_device_list_canonical",
    "_decode_device_status_canonical",
    "_decode_list_envelope_canonical",
    "_decode_mesh_group_status_canonical",
]
