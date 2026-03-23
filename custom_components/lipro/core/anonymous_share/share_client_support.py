"""Support-only helpers for anonymous-share share client mechanics."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Final, Protocol, TypedDict

from ..telemetry.models import OperationOutcome, build_operation_outcome

type SharePayload = dict[str, object]
type WorkerResponsePayload = dict[str, object]
type ResponseHeadersLike = Mapping[str, str]


class JsonReadableResponse(Protocol):
    """Minimal response surface for best-effort worker JSON reads."""

    def json(self, *, content_type: str | None = None) -> Awaitable[object] | object:
        """Return the decoded payload or one awaitable producing it."""


class TokenPayload(TypedDict, total=False):
    """Normalized token fields accepted from Worker responses."""

    install_token: str
    token_expires_at: int
    token_refresh_after: int


@dataclass(frozen=True, slots=True)
class SubmitVariant:
    """One payload-variant submit plan."""

    payload: SharePayload
    success_reason_code: str
    token_attempts: tuple[str | None, ...]
    fallback_on_payload_too_large: bool = False


def _coerce_int(value: object) -> int:
    """Normalize one token timestamp field into an int."""
    if value is None or isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return 0
        try:
            return int(text)
        except ValueError:
            return 0
    return 0


def _coerce_text(value: object) -> str | None:
    """Normalize one payload field into a non-empty string."""
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def extract_token_payload(payload: Mapping[str, object]) -> TokenPayload | None:
    """Return normalized install-token fields from one Worker payload."""
    token = payload.get("install_token")
    if not isinstance(token, str) or not token:
        return None

    normalized: TokenPayload = {"install_token": token}
    normalized["token_expires_at"] = _coerce_int(payload.get("token_expires_at"))
    normalized["token_refresh_after"] = _coerce_int(payload.get("token_refresh_after"))
    return normalized


def extract_response_code(payload: WorkerResponsePayload | None) -> str | None:
    """Return the canonical Worker response code from one payload."""
    if payload is None:
        return None
    code = payload.get("code")
    if isinstance(code, int):
        return str(code)
    return _coerce_text(code)


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


def has_valid_installation_id(report: Mapping[str, object]) -> bool:
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
    report: SharePayload,
    *,
    install_token: str | None,
    build_lite_variant: Callable[[SharePayload], SharePayload],
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


TOKEN_INVALID_CODES: Final[set[str]] = {
    "TOKEN_EXPIRED",
    "TOKEN_REVOKED",
    "TOKEN_VERSION_REVOKED",
    "TOKEN_KEY_NOT_FOUND",
    "TOKEN_SIGNATURE_INVALID",
    "TOKEN_CLAIMS_INVALID",
    "TOKEN_STATE_MISSING",
}

SUBMIT_TOKEN_REJECT_CODES: Final[set[str]] = {
    "TOKEN_VERSION_REVOKED",
    "TOKEN_REVOKED",
    "TOKEN_EXPIRED",
    "TOKEN_REQUIRED",
    "TOKEN_MISSING",
    "TOKEN_STATE_MISSING",
    "TOKEN_KEY_NOT_FOUND",
    "TOKEN_SIGNATURE_INVALID",
    "TOKEN_CLAIMS_INVALID",
    "TOKEN_INSTALLATION_MISMATCH",
}


def build_http_failure_outcome(
    *,
    failure_origin: str,
    http_status: int | None,
    reason_code: str = "http_error",
) -> OperationOutcome:
    """Build the canonical HTTP-failure outcome for share-client flows."""
    return build_operation_outcome(
        kind="failed",
        reason_code=reason_code,
        failure_origin=failure_origin,
        error_type=(f"HttpStatus{http_status}" if http_status is not None else None),
        failure_category="protocol",
        handling_policy="inspect",
        http_status=http_status,
    )


def build_rate_limited_outcome(
    *,
    failure_origin: str,
    retry_after_seconds: float | None,
) -> OperationOutcome:
    """Build the canonical rate-limited outcome for share-client flows."""
    return build_operation_outcome(
        kind="failed",
        reason_code="rate_limited",
        failure_origin=failure_origin,
        error_type="RateLimitError",
        failure_category="network",
        handling_policy="retry",
        http_status=429,
        retry_after_seconds=retry_after_seconds,
    )


def build_invalid_refresh_payload_outcome(*, failure_origin: str) -> OperationOutcome:
    """Build the invalid-refresh-payload outcome."""
    return build_operation_outcome(
        kind="failed",
        reason_code="invalid_refresh_payload",
        failure_origin=failure_origin,
        error_type="InvalidTokenPayload",
        failure_category="protocol",
        handling_policy="inspect",
        http_status=200,
    )


def build_token_invalid_outcome(*, failure_origin: str) -> OperationOutcome:
    """Build the canonical token-invalid outcome."""
    return build_operation_outcome(
        kind="failed",
        reason_code="token_invalid",
        failure_origin=failure_origin,
        error_type="InstallTokenRejected",
        failure_category="auth",
        handling_policy="reauth",
        http_status=401,
    )


def build_token_rejected_outcome(*, failure_origin: str) -> OperationOutcome:
    """Build the canonical token-rejected outcome."""
    return build_operation_outcome(
        kind="failed",
        reason_code="token_rejected",
        failure_origin=failure_origin,
        error_type="InstallTokenRejected",
        failure_category="auth",
        handling_policy="reauth",
        http_status=401,
    )


def build_invalid_schema_outcome(*, failure_origin: str) -> OperationOutcome:
    """Build the canonical invalid-schema outcome."""
    return build_operation_outcome(
        kind="failed",
        reason_code="invalid_schema",
        failure_origin=failure_origin,
        error_type="InvalidSchema",
        failure_category="protocol",
        handling_policy="inspect",
        http_status=400,
    )


def is_refresh_token_invalid(*, http_status: int, code: object) -> bool:
    """Return whether one refresh response invalidates the install token."""
    return http_status == 401 and isinstance(code, str) and code in TOKEN_INVALID_CODES


def is_submit_token_rejected(*, http_status: int, code: object) -> bool:
    """Return whether one submit response rejects the current install token."""
    return (
        http_status == 401
        and isinstance(code, str)
        and code in SUBMIT_TOKEN_REJECT_CODES
    )
