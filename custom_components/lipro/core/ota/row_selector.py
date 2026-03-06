"""OTA row scoring and selection helpers (no Home Assistant imports)."""

from __future__ import annotations

from typing import Any

from .manifest import first_text as _first_ota_text

_SERIAL_KEYS = ("deviceId", "serial", "iotId")
_DEVICE_TYPE_KEYS = (
    "deviceType",
    "iotType",
    "type",
    "fingerprint",
    "deviceFingerprint",
)
_IOT_NAME_KEYS = ("iotName", "fwIotName")
_PRODUCT_ID_KEYS = ("productId", "productID", "pid")
_PHYSICAL_MODEL_KEYS = ("physicalModel", "model", "productModel")
_LATEST_VERSION_KEYS = (
    "latestVersion",
    "latestFirmwareVersion",
    "targetVersion",
    "upgradeVersion",
)
_COMMON_VERSION_KEYS = ("firmwareVersion", "version")

_OTA_MATCH_SCORE_SERIAL_EXACT = 8
_OTA_MATCH_SCORE_BLE_NAME_EXACT = 6
_OTA_MATCH_SCORE_DEVICE_TYPE_EXACT = 4
_OTA_MATCH_SCORE_IOT_NAME_EXACT = 3
_OTA_MATCH_SCORE_PRODUCT_ID_EXACT = 3
_OTA_MATCH_SCORE_PHYSICAL_MODEL_EXACT = 2
_OTA_MATCH_SCORE_HAS_VERSION = 1


def score_exact_text_match(
    row: dict[str, Any],
    keys: tuple[str, ...],
    *,
    expected: str,
    weight: int,
    normalize: bool = True,
) -> int:
    """Return weight when OTA row text field matches expected value exactly."""
    value = _first_ota_text(row, keys)
    if value is None:
        return 0
    if normalize:
        return weight if value.lower() == expected else 0
    return weight if value == expected else 0


def score_row(
    row: dict[str, Any],
    *,
    serial: str,
    device_type: str,
    iot_name: str,
    product_id: str,
    physical_model: str,
) -> int:
    """Score one OTA row against the device fingerprint."""
    score = 0
    score += score_exact_text_match(
        row,
        _SERIAL_KEYS,
        expected=serial,
        weight=_OTA_MATCH_SCORE_SERIAL_EXACT,
    )
    score += score_exact_text_match(
        row,
        _DEVICE_TYPE_KEYS,
        expected=device_type,
        weight=_OTA_MATCH_SCORE_DEVICE_TYPE_EXACT,
    )
    score += score_exact_text_match(
        row,
        ("bleName",),
        expected=iot_name,
        weight=_OTA_MATCH_SCORE_BLE_NAME_EXACT,
    )
    score += score_exact_text_match(
        row,
        _IOT_NAME_KEYS,
        expected=iot_name,
        weight=_OTA_MATCH_SCORE_IOT_NAME_EXACT,
    )
    score += score_exact_text_match(
        row,
        _PRODUCT_ID_KEYS,
        expected=product_id,
        weight=_OTA_MATCH_SCORE_PRODUCT_ID_EXACT,
        normalize=False,
    )
    score += score_exact_text_match(
        row,
        _PHYSICAL_MODEL_KEYS,
        expected=physical_model,
        weight=_OTA_MATCH_SCORE_PHYSICAL_MODEL_EXACT,
    )
    if _first_ota_text(row, _LATEST_VERSION_KEYS + _COMMON_VERSION_KEYS) is not None:
        score += _OTA_MATCH_SCORE_HAS_VERSION
    return score


def select_best_row(
    rows: list[Any],
    *,
    serial: str,
    device_type: str,
    iot_name: str,
    product_id: str,
    physical_model: str,
) -> dict[str, Any] | None:
    """Pick the most relevant OTA row for a device."""
    if not rows:
        return None

    best_row: dict[str, Any] | None = None
    best_score = -1
    for row in rows:
        if not isinstance(row, dict):
            continue
        score = score_row(
            row,
            serial=serial,
            device_type=device_type,
            iot_name=iot_name,
            product_id=product_id,
            physical_model=physical_model,
        )
        if score > best_score:
            best_score = score
            best_row = row

    return best_row


def row_targets_other_device(
    row: dict[str, Any] | None, *, expected_serial: str
) -> bool:
    """Return True when selected row explicitly targets a different device."""
    if not isinstance(row, dict):
        return False
    expected = expected_serial.strip().lower()
    for key in _SERIAL_KEYS:
        raw = row.get(key)
        if not isinstance(raw, str):
            continue
        value = raw.strip().lower()
        if not value:
            continue
        return value != expected
    return False
