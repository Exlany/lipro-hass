"""OTA candidate normalization and install-policy helpers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import logging

from .candidate_support import (
    OtaInstallEvaluation,
    OtaManifestTruth,
    build_manifest_truth,
    consume_confirmation,
    evaluate_install,
    has_pending_confirmation,
    resolve_certification,
    resolve_inline_certification,
    resolve_local_manifest_certification,
    start_confirmation_window,
)
from .manifest import extract_install_command, first_bool, first_text

_LOGGER = logging.getLogger(__name__)

_LATEST_VERSION_KEYS = (
    "latestVersion",
    "latestFirmwareVersion",
    "targetVersion",
    "upgradeVersion",
)
_CURRENT_VERSION_KEYS = ("currentVersion", "currentFirmwareVersion")
_COMMON_VERSION_KEYS = ("firmwareVersion", "version")
_UPDATE_FLAG_KEYS = ("needUpgrade", "upgradeAvailable", "hasUpgrade", "hasUpdate")
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

type OtaRow = dict[str, object]
type OtaCommandProperty = dict[str, str]
type FirmwareManifestVersions = tuple[frozenset[str], dict[str, frozenset[str]]]

@dataclass(slots=True)
class _InstallCommand:
    """Normalized install command payload."""

    command: str
    properties: list[OtaCommandProperty] | None

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


@dataclass(frozen=True, slots=True)
class OtaCandidateProjection:
    """Projection payload consumed by the Home Assistant update entity."""

    installed_version: str | None
    latest_version: str | None
    release_summary: str | None
    release_url: str | None


def build_candidate(
    row: Mapping[str, object] | None,
    *,
    device_firmware_version: str | None,
    device_iot_name: str | None,
    local_manifest: FirmwareManifestVersions,
    is_version_newer: Callable[[str, str], bool],
) -> _OtaCandidate:
    """Normalize one OTA row into update-entity candidate metadata."""
    manifest_truth = build_manifest_truth(local_manifest)
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
        manifest_truth=manifest_truth,
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


def project_candidate(
    candidate: _OtaCandidate | None,
    *,
    current_installed_version: str | None,
) -> OtaCandidateProjection:
    """Project normalized OTA candidate metadata onto update-entity fields."""
    installed = current_installed_version
    latest = current_installed_version
    release_summary = None
    release_url = None

    if candidate is not None:
        installed = candidate.installed_version or current_installed_version
        latest = candidate.latest_version or installed
        release_summary = candidate.release_summary
        release_url = candidate.release_url

    return OtaCandidateProjection(
        installed_version=installed,
        latest_version=latest,
        release_summary=release_summary,
        release_url=release_url,
    )


def resolve_latest_version(
    row: Mapping[str, object] | None,
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
    row: Mapping[str, object] | None,
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
    except (
        AttributeError,
        LookupError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as err:
        _LOGGER.debug(
            "Unable to compare firmware versions (%s -> %s): %s",
            installed,
            latest,
            err,
        )
        return False


__all__ = [
    "OtaCandidateProjection",
    "OtaInstallEvaluation",
    "OtaManifestTruth",
    "_InstallCommand",
    "_OtaCandidate",
    "build_candidate",
    "consume_confirmation",
    "evaluate_install",
    "has_pending_confirmation",
    "project_candidate",
    "resolve_certification",
    "resolve_inline_certification",
    "resolve_latest_version",
    "resolve_local_manifest_certification",
    "resolve_update_available",
    "start_confirmation_window",
]
