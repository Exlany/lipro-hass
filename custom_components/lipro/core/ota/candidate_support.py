"""Internal OTA install-policy helpers with certification re-exports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from .candidate_certification_support import (
    OtaManifestTruth,
    build_manifest_truth,
    resolve_certification,
    resolve_inline_certification,
    resolve_local_manifest_certification,
)

if TYPE_CHECKING:
    from .candidate import _InstallCommand, _OtaCandidate


@dataclass(frozen=True, slots=True)
class OtaInstallEvaluation:
    """Result of validating one user-triggered install request."""

    install_command: _InstallCommand | None
    confirm_until: float
    error_key: str | None = None
    error_placeholders: dict[str, str] | None = None


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
    if candidate is not None and candidate.update_available:
        return None
    return OtaInstallEvaluation(
        install_command=None,
        confirm_until=confirm_until,
        error_key='firmware_no_update',
    )


def _evaluate_requested_version(
    candidate: _OtaCandidate,
    *,
    requested_version: str | None,
    confirm_until: float,
) -> OtaInstallEvaluation | None:
    if (
        requested_version is None
        or candidate.latest_version is None
        or requested_version == candidate.latest_version
    ):
        return None
    return OtaInstallEvaluation(
        install_command=None,
        confirm_until=confirm_until,
        error_key='firmware_version_mismatch',
        error_placeholders={'version': requested_version},
    )


def _evaluate_confirmation_window(
    candidate: _OtaCandidate,
    *,
    confirm_until: float,
    now_monotonic: float,
    confirmation_window_seconds: int,
) -> OtaInstallEvaluation | None:
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
        error_key='firmware_unverified_confirm_required',
        error_placeholders={'seconds': str(confirmation_window_seconds)},
    )


def _build_install_outcome(
    candidate: _OtaCandidate,
    *,
    confirm_until: float,
    now_monotonic: float,
) -> OtaInstallEvaluation:
    next_confirm_until = confirm_until
    if not candidate.certified:
        _confirmed, next_confirm_until = consume_confirmation(
            confirm_until,
            now_monotonic=now_monotonic,
        )
    if candidate.install_command is None:
        return OtaInstallEvaluation(
            install_command=None,
            confirm_until=next_confirm_until,
            error_key='firmware_install_unsupported',
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

    candidate = cast('_OtaCandidate', candidate)
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


__all__ = [
    'OtaInstallEvaluation',
    'OtaManifestTruth',
    'build_manifest_truth',
    'consume_confirmation',
    'evaluate_install',
    'has_pending_confirmation',
    'resolve_certification',
    'resolve_inline_certification',
    'resolve_local_manifest_certification',
    'start_confirmation_window',
]
