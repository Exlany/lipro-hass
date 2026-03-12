"""OTA candidate normalization helpers (no Home Assistant imports)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from .manifest import (
    build_manifest_type_candidates,
    extract_install_command,
    extract_version_set,
    first_bool,
    first_text,
    matches_certified_versions,
    matches_manifest_certification,
)

_LOGGER = logging.getLogger(__name__)

_IOT_NAME_KEYS = ("iotName", "fwIotName")
_LATEST_VERSION_KEYS = (
    "latestVersion",
    "latestFirmwareVersion",
    "targetVersion",
    "upgradeVersion",
)
_CURRENT_VERSION_KEYS = ("currentVersion", "currentFirmwareVersion")
_COMMON_VERSION_KEYS = ("firmwareVersion", "version")
_UPDATE_FLAG_KEYS = ("needUpgrade", "upgradeAvailable", "hasUpgrade", "hasUpdate")
_CERTIFIED_FLAG_KEYS = (
    "certified",
    "isCertified",
    "authPassed",
    "isAuthPassed",
    "approved",
)
_CERTIFIED_VERSION_KEYS = (
    "certifiedVersions",
    "certifiedVersionList",
    "certificationList",
    "authVersionList",
)
_RELEASE_SUMMARY_KEYS = ("releaseNotes", "releaseSummary", "description")
_RELEASE_URL_KEYS = ("releaseUrl", "releaseNoteUrl", "changelogUrl")
_COMMAND_CONTAINER_KEYS = (
    "upgradeCommand",
    "installCommand",
    "commandPayload",
    "upgradePayload",
)
_COMMAND_KEYS = ("command", "cmd", "name")
_COMMAND_PROPERTIES_KEYS = ("properties", "params", "arguments", "payload")


@dataclass(slots=True)
class _InstallCommand:
    """Normalized install command payload."""

    command: str
    properties: list[dict[str, str]] | None


@dataclass(slots=True)
class _OtaCandidate:
    """Normalized OTA candidate metadata."""

    installed_version: str | None
    latest_version: str | None
    update_available: bool
    certified: bool
    release_summary: str | None
    release_url: str | None
    install_command: _InstallCommand | None


def build_candidate(
    row: dict[str, Any] | None,
    *,
    device_firmware_version: str | None,
    device_iot_name: str | None,
    remote_verified_versions: frozenset[str],
    remote_versions_by_type: dict[str, frozenset[str]],
    local_verified_versions: frozenset[str],
    local_versions_by_type: dict[str, frozenset[str]],
    is_version_newer: Callable[[str, str], bool],
) -> _OtaCandidate:
    """Normalize one OTA row into update-entity candidate metadata."""
    installed = device_firmware_version or first_text(row, _CURRENT_VERSION_KEYS)
    latest = resolve_latest_version(row, installed)
    update_available = resolve_update_available(
        row,
        installed=installed,
        latest=latest,
        is_version_newer=is_version_newer,
    )
    certified = resolve_certification(
        row,
        installed=installed,
        latest=latest,
        device_iot_name=device_iot_name,
        remote_verified_versions=remote_verified_versions,
        remote_versions_by_type=remote_versions_by_type,
        local_verified_versions=local_verified_versions,
        local_versions_by_type=local_versions_by_type,
        is_version_newer=is_version_newer,
    )
    install_payload = extract_install_command(
        row,
        container_keys=_COMMAND_CONTAINER_KEYS,
        command_keys=_COMMAND_KEYS,
        properties_keys=_COMMAND_PROPERTIES_KEYS,
    )
    install_command = (
        _InstallCommand(
            command=install_payload[0],
            properties=install_payload[1],
        )
        if install_payload is not None
        else None
    )
    return _OtaCandidate(
        installed_version=installed,
        latest_version=latest,
        update_available=update_available,
        certified=certified,
        release_summary=first_text(row, _RELEASE_SUMMARY_KEYS),
        release_url=first_text(row, _RELEASE_URL_KEYS),
        install_command=install_command,
    )


def resolve_latest_version(
    row: dict[str, Any] | None,
    installed: str | None,
) -> str | None:
    """Resolve latest firmware version from OTA row."""
    latest = first_text(row, _LATEST_VERSION_KEYS)
    if latest is not None:
        return latest

    common = first_text(row, _COMMON_VERSION_KEYS)
    if common is None:
        return installed

    if installed is None or common != installed:
        return common
    return installed


def resolve_update_available(
    row: dict[str, Any] | None,
    *,
    installed: str | None,
    latest: str | None,
    is_version_newer: Callable[[str, str], bool],
) -> bool:
    """Resolve whether OTA update is available."""
    explicit_flag = first_bool(row, _UPDATE_FLAG_KEYS)
    if explicit_flag is not None:
        return explicit_flag

    if latest is None:
        return False
    if installed is None:
        return True
    if latest == installed:
        return False

    try:
        return bool(is_version_newer(latest, installed))
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug(
            "Unable to compare firmware versions (%s -> %s): %s",
            installed,
            latest,
            err,
        )
        # Be conservative on parse failures: avoid false positive upgrades.
        return False


def resolve_certification(
    row: dict[str, Any] | None,
    *,
    installed: str | None,
    latest: str | None,
    device_iot_name: str | None,
    remote_verified_versions: frozenset[str],
    remote_versions_by_type: dict[str, frozenset[str]],
    local_verified_versions: frozenset[str],
    local_versions_by_type: dict[str, frozenset[str]],
    is_version_newer: Callable[[str, str], bool],
) -> bool:
    """Resolve certification from inline data and local trust roots only."""
    del remote_verified_versions, remote_versions_by_type
    explicit_or_inline = resolve_inline_certification(
        row,
        installed=installed,
        latest=latest,
        is_version_newer=is_version_newer,
    )
    if explicit_or_inline is not None:
        return explicit_or_inline

    if latest is None:
        return False

    candidate_types = build_manifest_type_candidates(
        row,
        device_iot_name=device_iot_name,
        iot_name_keys=_IOT_NAME_KEYS,
    )
    return matches_manifest_certification(
        candidate_types,
        local_versions_by_type,
        local_verified_versions,
        installed=installed,
        latest=latest,
        is_version_newer=is_version_newer,
    )


def resolve_inline_certification(
    row: dict[str, Any] | None,
    *,
    installed: str | None,
    latest: str | None,
    is_version_newer: Callable[[str, str], bool],
) -> bool | None:
    """Resolve explicit certification flags and inline certification lists."""
    explicit_flag = first_bool(row, _CERTIFIED_FLAG_KEYS)
    if explicit_flag is not None:
        return explicit_flag

    certified_versions = extract_version_set(row, _CERTIFIED_VERSION_KEYS)
    if matches_certified_versions(
        certified_versions,
        installed=installed,
        latest=latest,
        is_version_newer=is_version_newer,
    ):
        return True

    certification_node = row.get("certification") if isinstance(row, dict) else None
    if not isinstance(certification_node, dict):
        return None

    node_flag = first_bool(certification_node, _CERTIFIED_FLAG_KEYS)
    if node_flag is not None:
        return node_flag

    node_versions = extract_version_set(certification_node, _CERTIFIED_VERSION_KEYS)
    if matches_certified_versions(
        node_versions,
        installed=installed,
        latest=latest,
        is_version_newer=is_version_newer,
    ):
        return True
    return None
