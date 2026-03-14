"""OTA candidate normalization and install-policy helpers."""

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

type FirmwareManifestVersions = tuple[frozenset[str], dict[str, frozenset[str]]]


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


@dataclass(frozen=True, slots=True)
class OtaCandidateProjection:
    """Projection payload consumed by the Home Assistant update entity."""

    installed_version: str | None
    latest_version: str | None
    release_summary: str | None
    release_url: str | None


@dataclass(frozen=True, slots=True)
class OtaInstallEvaluation:
    """Result of validating one user-triggered install request."""

    install_command: _InstallCommand | None
    confirm_until: float
    error_key: str | None = None
    error_placeholders: dict[str, str] | None = None


@dataclass(frozen=True, slots=True)
class OtaManifestTruth:
    """Bundled manifest truth used for certification arbitration."""

    verified_versions: frozenset[str]
    versions_by_type: dict[str, frozenset[str]]


def _build_manifest_truth(
    local_manifest: FirmwareManifestVersions,
) -> OtaManifestTruth:
    verified_versions, versions_by_type = local_manifest
    return OtaManifestTruth(
        verified_versions=verified_versions,
        versions_by_type=versions_by_type,
    )


def build_candidate(
    row: dict[str, Any] | None,
    *,
    device_firmware_version: str | None,
    device_iot_name: str | None,
    local_manifest: FirmwareManifestVersions,
    is_version_newer: Callable[[str, str], bool],
) -> _OtaCandidate:
    """Normalize one OTA row into update-entity candidate metadata."""
    manifest_truth = _build_manifest_truth(local_manifest)
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


def has_pending_confirmation(
    confirm_until: float,
    *,
    now_monotonic: float,
) -> bool:
    """Return whether unverified-install confirmation window is active."""
    return now_monotonic < confirm_until


def start_confirmation_window(
    *,
    now_monotonic: float,
    confirmation_window_seconds: int,
) -> float:
    """Return deadline for one new unverified-install confirmation window."""
    return now_monotonic + confirmation_window_seconds


def consume_confirmation(
    confirm_until: float,
    *,
    now_monotonic: float,
) -> tuple[bool, float]:
    """Consume one pending confirmation window when it is still active."""
    if not has_pending_confirmation(confirm_until, now_monotonic=now_monotonic):
        return False, confirm_until
    return True, 0.0


def evaluate_install(
    candidate: _OtaCandidate | None,
    *,
    requested_version: str | None,
    confirm_until: float,
    now_monotonic: float,
    confirmation_window_seconds: int,
) -> OtaInstallEvaluation:
    """Validate install intent and return the install/confirmation decision."""
    if candidate is None or not candidate.update_available:
        return OtaInstallEvaluation(
            install_command=None,
            confirm_until=confirm_until,
            error_key="firmware_no_update",
        )

    if (
        requested_version is not None
        and candidate.latest_version is not None
        and requested_version != candidate.latest_version
    ):
        return OtaInstallEvaluation(
            install_command=None,
            confirm_until=confirm_until,
            error_key="firmware_version_mismatch",
            error_placeholders={"version": requested_version},
        )

    next_confirm_until = confirm_until
    if not candidate.certified:
        confirmed, next_confirm_until = consume_confirmation(
            confirm_until,
            now_monotonic=now_monotonic,
        )
        if not confirmed:
            next_confirm_until = start_confirmation_window(
                now_monotonic=now_monotonic,
                confirmation_window_seconds=confirmation_window_seconds,
            )
            return OtaInstallEvaluation(
                install_command=None,
                confirm_until=next_confirm_until,
                error_key="firmware_unverified_confirm_required",
                error_placeholders={"seconds": str(confirmation_window_seconds)},
            )

    if candidate.install_command is None:
        return OtaInstallEvaluation(
            install_command=None,
            confirm_until=next_confirm_until,
            error_key="firmware_install_unsupported",
        )

    return OtaInstallEvaluation(
        install_command=candidate.install_command,
        confirm_until=next_confirm_until,
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
        return False


def resolve_certification(
    row: dict[str, Any] | None,
    *,
    installed: str | None,
    latest: str | None,
    device_iot_name: str | None,
    manifest_truth: OtaManifestTruth,
    is_version_newer: Callable[[str, str], bool],
) -> bool:
    """Resolve certification from inline data and the bundled manifest truth."""
    explicit_or_inline = resolve_inline_certification(
        row,
        installed=installed,
        latest=latest,
        is_version_newer=is_version_newer,
    )
    if explicit_or_inline is not None:
        return explicit_or_inline

    return resolve_local_manifest_certification(
        row,
        installed=installed,
        latest=latest,
        device_iot_name=device_iot_name,
        manifest_truth=manifest_truth,
        is_version_newer=is_version_newer,
    )


def resolve_local_manifest_certification(
    row: dict[str, Any] | None,
    *,
    installed: str | None,
    latest: str | None,
    device_iot_name: str | None,
    manifest_truth: OtaManifestTruth,
    is_version_newer: Callable[[str, str], bool],
) -> bool:
    """Resolve certification using only the bundled local manifest authority."""
    if latest is None:
        return False

    candidate_types = build_manifest_type_candidates(
        row,
        device_iot_name=device_iot_name,
        iot_name_keys=_IOT_NAME_KEYS,
    )
    return matches_manifest_certification(
        candidate_types,
        manifest_truth.versions_by_type,
        manifest_truth.verified_versions,
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
