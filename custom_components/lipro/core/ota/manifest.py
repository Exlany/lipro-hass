"""Shared OTA payload normalization helpers."""

from __future__ import annotations

from collections.abc import Callable, Collection, Mapping, Sequence
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


def parse_ota_boollike(value: Any) -> bool | None:
    """Parse OTA bool-like values or return ``None`` when unknown."""
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
        normalized = parse_ota_boollike(data.get(key))
        if normalized is not None:
            return normalized
    return None


def append_unique_normalized(target: list[str], value: str | None) -> None:
    """Append one normalized key if valid and non-duplicate."""
    if value is None:
        return
    normalized = value.strip().lower()
    if normalized and normalized not in target:
        target.append(normalized)


def build_manifest_type_candidates(
    row: dict[str, Any] | None,
    *,
    device_iot_name: str | None,
    iot_name_keys: tuple[str, ...] = MANIFEST_TYPE_KEY_PRIORITY[1],
    ble_name_key: str = "bleName",
) -> list[str]:
    """Build locked candidate keys for manifest.type matching.

    Lock rule:
    - Controller rows only use bleName.
    - Device rows only use iotName (and may fall back to device metadata).
    """
    candidates: list[str] = []

    row_ble_name = first_text(row, (ble_name_key,))
    if row_ble_name is not None:
        append_unique_normalized(candidates, row_ble_name)
        return candidates

    row_iot_name = first_text(row, iot_name_keys)
    resolved_iot_name = device_iot_name or row_iot_name
    append_unique_normalized(candidates, row_iot_name)
    append_unique_normalized(candidates, resolved_iot_name)
    return candidates


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

        if parse_ota_boollike(row.get("certified")) is not True:
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


def extract_version_set(
    data: dict[str, Any] | None,
    keys: tuple[str, ...],
) -> set[str]:
    """Extract firmware versions from arbitrary list fields."""
    if not isinstance(data, dict):
        return set()

    versions: set[str] = set()
    for key in keys:
        versions.update(normalize_version_list(data.get(key)))
    return versions


def matches_certified_versions(
    certified_versions: Collection[str],
    *,
    installed: str | None,
    latest: str | None,
    is_version_newer: Callable[[str, str], bool],
) -> bool:
    """Return True when certification list authorizes current upgrade."""
    if not certified_versions:
        return False

    # Keep exact-target match for deterministic OTA payloads.
    if latest and latest in certified_versions:
        return True

    # Relaxed rule: any certified version newer than current firmware
    # means this device generation is considered certified for upgrade.
    if installed is None:
        return False
    return any(
        is_version_newer(candidate, installed) for candidate in certified_versions
    )


def matches_manifest_certification(
    candidate_types: Sequence[str],
    versions_by_type: Mapping[str, Collection[str]],
    fallback_versions: Collection[str],
    *,
    installed: str | None,
    latest: str | None,
    is_version_newer: Callable[[str, str], bool],
) -> bool:
    """Match certification from typed manifest versions with global fallback."""
    has_type_match = False
    for candidate in candidate_types:
        type_versions = versions_by_type.get(candidate)
        if type_versions is None:
            continue
        has_type_match = True
        if matches_certified_versions(
            type_versions,
            installed=installed,
            latest=latest,
            is_version_newer=is_version_newer,
        ):
            return True

    if has_type_match:
        return False

    return matches_certified_versions(
        fallback_versions,
        installed=installed,
        latest=latest,
        is_version_newer=is_version_newer,
    )


def _coerce_property_pair(raw_key: Any, raw_value: Any) -> dict[str, str] | None:
    """Build one normalized command property pair."""
    if raw_key is None or raw_value is None:
        return None
    return {"key": str(raw_key), "value": str(raw_value)}


def coerce_command_properties(value: Any) -> list[dict[str, str]] | None:
    """Coerce a command properties payload to a key/value list."""
    if value is None:
        return None

    if isinstance(value, dict):
        properties: list[dict[str, str]] = []
        for key, item in value.items():
            property_item = _coerce_property_pair(key, item)
            if property_item is not None:
                properties.append(property_item)
        return properties or None

    if not isinstance(value, list):
        return None

    result: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        property_item = _coerce_property_pair(item.get("key"), item.get("value"))
        if property_item is not None:
            result.append(property_item)
    return result or None


def normalize_command_properties(
    payload: dict[str, Any],
    *,
    properties_keys: tuple[str, ...],
) -> list[dict[str, str]] | None:
    """Normalize command properties payload to key/value list."""
    for key in properties_keys:
        normalized = coerce_command_properties(payload.get(key))
        if normalized is not None:
            return normalized
    return None


def parse_install_command_payload(
    payload: Any,
    *,
    command_keys: tuple[str, ...],
    properties_keys: tuple[str, ...],
) -> tuple[str, list[dict[str, str]] | None] | None:
    """Parse install command payload from nested or top-level OTA fields."""
    if isinstance(payload, str):
        command_text = payload.strip()
        return (command_text, None) if command_text else None

    if not isinstance(payload, dict):
        return None

    command = first_text(payload, command_keys)
    if command is None:
        return None

    return (
        command,
        normalize_command_properties(payload, properties_keys=properties_keys),
    )


def extract_install_command(
    row: dict[str, Any] | None,
    *,
    container_keys: tuple[str, ...],
    command_keys: tuple[str, ...],
    properties_keys: tuple[str, ...],
) -> tuple[str, list[dict[str, str]] | None] | None:
    """Extract install command payload from OTA row."""
    if not isinstance(row, dict):
        return None

    for key in container_keys:
        parsed = parse_install_command_payload(
            row.get(key),
            command_keys=command_keys,
            properties_keys=properties_keys,
        )
        if parsed is not None:
            return parsed

    return parse_install_command_payload(
        row,
        command_keys=command_keys,
        properties_keys=properties_keys,
    )

