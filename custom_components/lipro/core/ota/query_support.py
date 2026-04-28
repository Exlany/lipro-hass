"""Shared OTA query row helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import cast

from ..api.types import JsonObject, JsonValue, OtaInfoRow

RequestPayload = JsonObject
OtaRowDedupeKey = tuple[str, str, str, str, str]


def _build_rich_ota_v2_payload(
    ota_payload: Mapping[str, JsonValue],
    *,
    iot_name: str | None,
    allow_rich_v2_fallback: bool,
) -> RequestPayload | None:
    """Build richer OTA v2 payload for devices that benefit from hasMacRule."""
    if not allow_rich_v2_fallback:
        return None
    normalized_iot_name = str(iot_name or "").strip()
    if not normalized_iot_name:
        return None
    return {
        **dict(ota_payload),
        "iotName": normalized_iot_name,
        "skuId": "",
        "hasMacRule": True,
    }


def _ota_row_dedupe_key(row: Mapping[str, object]) -> OtaRowDedupeKey:
    """Build stable dedupe key for one OTA row."""
    return (
        str(row.get("deviceId") or row.get("iotId") or "").strip().lower(),
        str(row.get("deviceType") or row.get("bleName") or row.get("productName") or "")
        .strip()
        .lower(),
        str(
            row.get("latestVersion")
            or row.get("firmwareVersion")
            or row.get("version")
            or ""
        )
        .strip()
        .lower(),
        str(row.get("firmwareUrl") or row.get("url") or "").strip().lower(),
        str(row.get("md5") or "").strip().lower(),
    )


def _merge_ota_rows(
    merged_rows: list[OtaInfoRow],
    seen_keys: set[OtaRowDedupeKey],
    rows: Sequence[object],
) -> None:
    """Merge OTA rows in order while dropping duplicates by semantic key."""
    for row in rows:
        if not isinstance(row, dict):
            continue
        key = _ota_row_dedupe_key(row)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        merged_rows.append(cast(OtaInfoRow, row))


def _build_seen_ota_row_keys(rows: Sequence[OtaInfoRow]) -> set[OtaRowDedupeKey]:
    """Build the dedupe-key set for already merged OTA rows."""
    return {_ota_row_dedupe_key(row) for row in rows}
