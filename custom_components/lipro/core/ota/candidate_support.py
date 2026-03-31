"""Internal OTA certification and install-policy helpers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

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


def _evaluate_update_availability(
    candidate: _OtaCandidate | None,
    *,
    confirm_until: float,
) -> OtaInstallEvaluation | None:
    """Reject install attempts when no upgrade candidate is currently available."""
    if candidate is not None and candidate.update_available:
        return None
    return OtaInstallEvaluation(
        install_command=None,
        confirm_until=confirm_until,
        error_key="firmware_no_update",
    )


def _evaluate_requested_version(
    candidate: _OtaCandidate,
    *,
    requested_version: str | None,
    confirm_until: float,
) -> OtaInstallEvaluation | None:
    """Reject install requests that target a different version than the candidate."""
    if (
        requested_version is None
        or candidate.latest_version is None
        or requested_version == candidate.latest_version
    ):
        return None
    return OtaInstallEvaluation(
        install_command=None,
        confirm_until=confirm_until,
        error_key="firmware_version_mismatch",
        error_placeholders={"version": requested_version},
    )


def _evaluate_confirmation_window(
    candidate: _OtaCandidate,
    *,
    confirm_until: float,
    now_monotonic: float,
    confirmation_window_seconds: int,
) -> OtaInstallEvaluation | None:
    """Require explicit confirmation before unverified installs proceed."""
    if candidate.certified:
        return None

    confirmed, next_confirm_until = consume_confirmation(
        confirm_until,
        now_monotonic=now_monotonic,
    )
    if confirmed:
        return None

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


def _resolve_install_confirmation_deadline(
    candidate: _OtaCandidate,
    *,
    confirm_until: float,
    now_monotonic: float,
) -> float:
    """Return the post-validation confirmation deadline for a permitted install."""
    if candidate.certified:
        return confirm_until
    _confirmed, next_confirm_until = consume_confirmation(
        confirm_until,
        now_monotonic=now_monotonic,
    )
    return next_confirm_until


def _build_install_outcome(
    candidate: _OtaCandidate,
    *,
    confirm_until: float,
    now_monotonic: float,
) -> OtaInstallEvaluation:
    """Return the final install outcome after all policy gates have passed."""
    next_confirm_until = _resolve_install_confirmation_deadline(
        candidate,
        confirm_until=confirm_until,
        now_monotonic=now_monotonic,
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


def evaluate_install(
    candidate: _OtaCandidate | None,
    *,
    requested_version: str | None,
    confirm_until: float,
    now_monotonic: float,
    confirmation_window_seconds: int,
) -> OtaInstallEvaluation:
    """Validate install intent and return the install/confirmation decision."""
    no_update = _evaluate_update_availability(
        candidate,
        confirm_until=confirm_until,
    )
    if no_update is not None:
        return no_update

    candidate = cast("_OtaCandidate", candidate)
    version_mismatch = _evaluate_requested_version(
        candidate,
        requested_version=requested_version,
        confirm_until=confirm_until,
    )
    if version_mismatch is not None:
        return version_mismatch

    confirmation_required = _evaluate_confirmation_window(
        candidate,
        confirm_until=confirm_until,
        now_monotonic=now_monotonic,
        confirmation_window_seconds=confirmation_window_seconds,
    )
    if confirmation_required is not None:
        return confirmation_required

    return _build_install_outcome(
        candidate,
        confirm_until=confirm_until,
        now_monotonic=now_monotonic,
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
