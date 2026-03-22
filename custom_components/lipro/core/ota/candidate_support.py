"""Internal OTA certification and install-policy helpers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .manifest import (
    build_manifest_type_candidates,
    extract_version_set,
    first_bool,
    matches_certified_versions,
    matches_manifest_certification,
)

if TYPE_CHECKING:
    from .candidate import _InstallCommand, _OtaCandidate

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

_IOT_NAME_KEYS = ("iotName", "fwIotName")


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


def build_manifest_truth(
    local_manifest: tuple[frozenset[str], dict[str, frozenset[str]]],
) -> OtaManifestTruth:
    """Wrap local manifest tuples into the certification-truth dataclass."""
    verified_versions, versions_by_type = local_manifest
    return OtaManifestTruth(
        verified_versions=verified_versions,
        versions_by_type=versions_by_type,
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


def resolve_certification(
    row: Mapping[str, object] | None,
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
    row: Mapping[str, object] | None,
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
    row: Mapping[str, object] | None,
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

    certification_node = row.get("certification") if isinstance(row, Mapping) else None
    if not isinstance(certification_node, Mapping):
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
