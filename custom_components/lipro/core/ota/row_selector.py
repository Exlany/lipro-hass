"""OTA row scoring, selection, and cache-arbitration helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

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

type OtaRow = dict[str, object]


@dataclass(frozen=True, slots=True)
class OtaDeviceFingerprint:
    """Normalized device identity used for OTA row selection."""

    serial: str
    device_type: str
    iot_name: str
    product_id: str
    physical_model: str


@dataclass(frozen=True, slots=True)
class OtaRowArbitration:
    """Selection result with cache-bypass guidance."""

    selected_row: OtaRow | None
    should_retry_without_cache: bool


def build_device_fingerprint(
    *,
    serial: str,
    device_type: str,
    iot_name: str | None,
    product_id: int | str | None,
    physical_model: str | None,
) -> OtaDeviceFingerprint:
    """Build one normalized fingerprint for OTA row selection."""
    return OtaDeviceFingerprint(
        serial=serial.strip().lower(),
        device_type=device_type.strip().lower(),
        iot_name=str(iot_name or "").strip().lower(),
        product_id=str(product_id or ""),
        physical_model=str(physical_model or "").strip().lower(),
    )


def score_exact_text_match(
    row: Mapping[str, object],
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
    row: Mapping[str, object],
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
    rows: Sequence[object],
    *,
    serial: str,
    device_type: str,
    iot_name: str,
    product_id: str,
    physical_model: str,
) -> OtaRow | None:
    """Pick the most relevant OTA row for a device."""
    if not rows:
        return None

    best_row: OtaRow | None = None
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


def select_best_row_for_device(
    rows: Sequence[object],
    *,
    fingerprint: OtaDeviceFingerprint,
) -> OtaRow | None:
    """Pick the best OTA row for one normalized device fingerprint."""
    return select_best_row(
        rows,
        serial=fingerprint.serial,
        device_type=fingerprint.device_type,
        iot_name=fingerprint.iot_name,
        product_id=fingerprint.product_id,
        physical_model=fingerprint.physical_model,
    )


def arbitrate_rows(
    rows: Sequence[object],
    *,
    fingerprint: OtaDeviceFingerprint,
    from_cache: bool,
) -> OtaRowArbitration:
    """Select one OTA row and decide whether cache should be bypassed."""
    selected_row = select_best_row_for_device(rows, fingerprint=fingerprint)
    return OtaRowArbitration(
        selected_row=selected_row,
        should_retry_without_cache=(
            from_cache
            and row_targets_other_device(
                selected_row,
                expected_serial=fingerprint.serial,
            )
        ),
    )


def row_targets_other_device(
    row: Mapping[str, object] | None,
    *,
    expected_serial: str,
) -> bool:
    """Return True when selected row explicitly targets a different device."""
    if row is None:
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
