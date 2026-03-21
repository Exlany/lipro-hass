"""Support-only helpers for anonymous-share share client mechanics."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SubmitVariant:
    """One payload-variant submit plan."""

    payload: dict[str, Any]
    success_reason_code: str
    token_attempts: tuple[str | None, ...]
    fallback_on_payload_too_large: bool = False


def backoff_active(
    *,
    next_upload_attempt_at: float,
    now: Callable[[], float],
) -> bool:
    """Return whether upload/refresh backoff is still active."""
    return now() < next_upload_attempt_at


def schedule_retry_deadline(
    *,
    retry_after_seconds: float | None,
    now: Callable[[], float],
) -> float | None:
    """Return the next upload-at deadline for rate-limited responses."""
    if retry_after_seconds is None:
        return None
    return now() + min(60.0, retry_after_seconds)


def has_valid_installation_id(report: dict[str, Any]) -> bool:
    """Return whether the payload contains a usable installation id."""
    installation_id = report.get("installation_id")
    return isinstance(installation_id, str) and bool(installation_id)


def refresh_due(
    *,
    install_token: str | None,
    token_refresh_after: int,
    token_expires_at: int,
    now_seconds: int,
) -> bool:
    """Return whether the install token should be refreshed before submit."""
    if not install_token:
        return False
    if token_refresh_after and now_seconds >= token_refresh_after:
        return True
    if token_expires_at and (token_expires_at - now_seconds) <= 60:
        return True
    return False


def build_submit_variants(
    report: dict[str, Any],
    *,
    install_token: str | None,
    build_lite_variant: Callable[[dict[str, Any]], dict[str, Any]],
) -> tuple[SubmitVariant, ...]:
    """Build full/lite submit variants with the correct token attempts."""
    token_attempts = (install_token, None) if install_token else (None,)
    return (
        SubmitVariant(
            payload=report,
            success_reason_code="submitted",
            token_attempts=token_attempts,
            fallback_on_payload_too_large=True,
        ),
        SubmitVariant(
            payload=build_lite_variant(report),
            success_reason_code="submitted_lite_payload",
            token_attempts=token_attempts,
        ),
    )


def submit_failure_reason_code(http_status: int | None) -> str:
    """Return the canonical submit failure reason code for a terminal status."""
    return "payload_too_large" if http_status == 413 else "http_error"
