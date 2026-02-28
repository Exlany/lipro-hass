"""Shared OTA payload normalization helpers."""

from __future__ import annotations

from collections.abc import Callable
import json
from pathlib import Path
from typing import Any

DEFAULT_OTA_VERSION_KEYS: tuple[str, ...] = (
    "latestVersion",
    "latestFirmwareVersion",
    "targetVersion",
    "upgradeVersion",
    "firmwareVersion",
    "version",
)
MANIFEST_TYPE_KEY_PRIORITY: tuple[tuple[str, ...], ...] = (
    ("bleName",),
    ("iotName", "fwIotName"),
)


def first_text(data: dict[str, Any] | None, keys: tuple[str, ...]) -> str | None:
    """Return first non-empty text value for any key."""
    if not isinstance(data, dict):
        return None
    for key in keys:
        value = data.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def coerce_boollike(value: Any) -> bool | None:
    """Parse bool-like values or return ``None`` when unknown."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        if value in (0, 1):
            return bool(value)
        return None
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on", "certified", "passed"}:
            return True
        if normalized in {"0", "false", "no", "off", "uncertified", "failed"}:
            return False
    return None


def first_bool(data: dict[str, Any] | None, keys: tuple[str, ...]) -> bool | None:
    """Return first bool-like field value from payload."""
    if not isinstance(data, dict):
        return None
    for key in keys:
        normalized = coerce_boollike(data.get(key))
        if normalized is not None:
            return normalized
    return None


def normalize_version_list(value: Any) -> frozenset[str]:
    """Normalize one firmware-version list field."""
    if not isinstance(value, list):
        return frozenset()
    return frozenset(text for item in value if (text := str(item).strip()))


def normalize_versions_by_type(value: Any) -> dict[str, frozenset[str]]:
    """Normalize version map by device type from manifest payload."""
    if not isinstance(value, dict):
        return {}

    result: dict[str, frozenset[str]] = {}
    for raw_type, raw_versions in value.items():
        if not isinstance(raw_type, str):
            continue
        normalized_type = raw_type.strip().lower()
        if not normalized_type:
            continue
        normalized_versions = normalize_version_list(raw_versions)
        if normalized_versions:
            result[normalized_type] = normalized_versions
    return result


def parse_verified_firmware_manifest_payload(
    payload: Any,
) -> tuple[frozenset[str], dict[str, frozenset[str]]]:
    """Parse firmware support manifest payload."""
    if isinstance(payload, list):
        return normalize_version_list(payload), {}

    if not isinstance(payload, dict):
        return frozenset(), {}

    firmware_list = payload.get("firmware_list")
    if isinstance(firmware_list, list):
        return _derive_verified_versions_from_firmware_list(firmware_list)

    return (
        normalize_version_list(payload.get("verified_versions")),
        normalize_versions_by_type(payload.get("verified_versions_by_type")),
    )


def _derive_verified_versions_from_firmware_list(
    rows: list[Any],
) -> tuple[frozenset[str], dict[str, frozenset[str]]]:
    """Derive verified version sets from firmware_list rows."""
    derived_versions: set[str] = set()
    derived_by_type: dict[str, set[str]] = {}

    for row in rows:
        if not isinstance(row, dict):
            continue

        version = first_text(row, DEFAULT_OTA_VERSION_KEYS)
        if version is None:
            continue

        if coerce_boollike(row.get("certified")) is not True:
            continue

        derived_versions.add(version)
        for key_group in MANIFEST_TYPE_KEY_PRIORITY:
            candidate = first_text(row, key_group)
            if candidate is None:
                continue
            normalized = candidate.strip().lower()
            if normalized:
                derived_by_type.setdefault(normalized, set()).add(version)
                # Lock rule: controller uses bleName first.
                if key_group == MANIFEST_TYPE_KEY_PRIORITY[0]:
                    break

    return frozenset(derived_versions), {
        key: frozenset(values) for key, values in derived_by_type.items() if values
    }


def load_verified_firmware_manifest_file(
    manifest_path: Path,
    *,
    on_error: Callable[[Path, OSError | json.JSONDecodeError], None],
) -> tuple[frozenset[str], dict[str, frozenset[str]]]:
    """Load and parse one firmware support manifest file."""
    try:
        content = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        on_error(manifest_path, err)
        return frozenset(), {}

    return parse_verified_firmware_manifest_payload(content)


def extract_ota_versions(
    rows: Any,
    *,
    version_keys: tuple[str, ...] = DEFAULT_OTA_VERSION_KEYS,
) -> set[str]:
    """Extract normalized firmware versions from OTA rows."""
    if not isinstance(rows, list):
        return set()

    versions: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key in version_keys:
            value = row.get(key)
            if value is None:
                continue
            text = str(value).strip()
            if text:
                versions.add(text)
    return versions
