"""Inward telemetry failure/outcome helpers behind the outward contract home."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal, NotRequired, TypedDict

type FailureCategory = Literal["auth", "network", "protocol", "runtime", "unexpected"]
type HandlingPolicy = Literal["reauth", "retry", "inspect", "escalate"]
type OutcomeKind = Literal["success", "skipped", "degraded", "failed"]
type TelemetryReadablePayload = Mapping[str, object]


class FailureSummary(TypedDict):
    """Canonical failure-summary payload shared across telemetry views."""

    failure_category: FailureCategory | None
    failure_origin: str | None
    handling_policy: HandlingPolicy | None
    error_type: str | None


class OperationOutcomePayload(TypedDict):
    """Stable mapping form for one operation outcome."""

    outcome_kind: OutcomeKind
    reason_code: str
    failure_summary: NotRequired[FailureSummary]
    http_status: NotRequired[int]
    retry_after_seconds: NotRequired[float]


_NETWORK_ERROR_MARKERS = (
    "timeout",
    "disconnect",
    "connect",
    "network",
    "socket",
    "connection",
    "clienterror",
    "serverdisconnected",
    "oserror",
)
_AUTH_ERROR_MARKERS = (
    "auth",
    "token",
    "credential",
    "login",
    "permission",
    "forbidden",
    "unauthorized",
)
_PROTOCOL_ERROR_MARKERS = (
    "value",
    "parse",
    "decode",
    "encode",
    "schema",
    "protocol",
    "payload",
    "json",
    "keyerror",
)
_RUNTIME_ERROR_MARKERS = (
    "runtime",
    "cancel",
    "state",
    "attribute",
)


def empty_failure_summary() -> FailureSummary:
    """Return the canonical empty failure-summary shape."""
    return {
        "failure_category": None,
        "failure_origin": None,
        "handling_policy": None,
        "error_type": None,
    }


def _coerce_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def classify_failure_category(error_type: str | None) -> FailureCategory | None:
    """Map one raw error type into the shared failure taxonomy."""
    if error_type is None:
        return None
    normalized = error_type.casefold()
    if any(marker in normalized for marker in _AUTH_ERROR_MARKERS):
        return "auth"
    if any(marker in normalized for marker in _NETWORK_ERROR_MARKERS):
        return "network"
    if any(marker in normalized for marker in _PROTOCOL_ERROR_MARKERS):
        return "protocol"
    if any(marker in normalized for marker in _RUNTIME_ERROR_MARKERS):
        return "runtime"
    return "unexpected"


def handling_policy_for_category(
    category: FailureCategory | None,
) -> HandlingPolicy | None:
    """Return the preferred handling policy for one normalized category."""
    if category == "auth":
        return "reauth"
    if category == "network":
        return "retry"
    if category in {"protocol", "runtime"}:
        return "inspect"
    if category == "unexpected":
        return "escalate"
    return None


def _normalize_failure_category(
    category: str | None,
) -> FailureCategory | None:
    """Return one accepted failure category literal when the input matches it."""
    if category == "auth":
        return "auth"
    if category == "network":
        return "network"
    if category == "protocol":
        return "protocol"
    if category == "runtime":
        return "runtime"
    if category == "unexpected":
        return "unexpected"
    return None


def _normalize_handling_policy(
    handling_policy: str | None,
) -> HandlingPolicy | None:
    """Return one accepted handling-policy literal when the input matches it."""
    if handling_policy == "reauth":
        return "reauth"
    if handling_policy == "retry":
        return "retry"
    if handling_policy == "inspect":
        return "inspect"
    if handling_policy == "escalate":
        return "escalate"
    return None


def build_failure_summary(
    *,
    error_type: str | None,
    failure_origin: str | None,
    failure_category: str | None = None,
    handling_policy: str | None = None,
) -> FailureSummary:
    """Build the canonical failure-summary payload."""
    normalized_category = _normalize_failure_category(
        failure_category
    ) or classify_failure_category(error_type)
    normalized_policy = _normalize_handling_policy(
        handling_policy
    ) or handling_policy_for_category(normalized_category)
    normalized_origin = failure_origin if error_type is not None else None
    if normalized_category is None and error_type is None:
        normalized_origin = None
        normalized_policy = None
    return {
        "failure_category": normalized_category,
        "failure_origin": normalized_origin,
        "handling_policy": normalized_policy,
        "error_type": error_type,
    }


def build_failure_summary_from_exception(
    err: BaseException | None,
    *,
    failure_origin: str,
    failure_category: str | None = None,
    handling_policy: str | None = None,
) -> FailureSummary:
    """Build one failure summary from a concrete exception instance."""
    error_type = type(err).__name__ if err is not None else None
    return build_failure_summary(
        error_type=error_type,
        failure_origin=failure_origin,
        failure_category=failure_category,
        handling_policy=handling_policy,
    )


def extract_failure_summary(
    payload: TelemetryReadablePayload | object,
    *,
    default_origin: str,
    raw_error_keys: tuple[str, ...],
) -> FailureSummary:
    """Return explicit failure_summary when present, else derive from raw fields."""
    if not isinstance(payload, Mapping):
        return empty_failure_summary()

    explicit = payload.get("failure_summary")
    summary_payload = explicit if isinstance(explicit, Mapping) else payload
    error_type = _coerce_text(summary_payload.get("error_type")) or _coerce_text(
        summary_payload.get("raw_error_type")
    )
    if error_type is None:
        for key in raw_error_keys:
            error_type = _coerce_text(summary_payload.get(key))
            if error_type is not None:
                break

    failure_category = _coerce_text(summary_payload.get("failure_category"))
    failure_origin = _coerce_text(summary_payload.get("failure_origin"))
    handling_policy = _coerce_text(summary_payload.get("handling_policy"))
    if failure_origin is None and (failure_category is not None or error_type is not None):
        failure_origin = default_origin
    return build_failure_summary(
        error_type=error_type,
        failure_origin=failure_origin,
        failure_category=failure_category,
        handling_policy=handling_policy,
    )


@dataclass(frozen=True, slots=True)
class OperationOutcome:
    """Typed, machine-consumable operation result shared across hotspots."""

    kind: OutcomeKind
    reason_code: str
    failure_summary: FailureSummary = field(default_factory=empty_failure_summary)
    http_status: int | None = None
    retry_after_seconds: float | None = None

    @property
    def is_success(self) -> bool:
        """Return whether the outcome represents one successful operation."""
        return self.kind == "success"

    def to_dict(self) -> OperationOutcomePayload:
        """Return the canonical mapping form used by service responses/tests."""
        result: OperationOutcomePayload = {
            "outcome_kind": self.kind,
            "reason_code": self.reason_code,
        }
        if any(value is not None for value in self.failure_summary.values()):
            result["failure_summary"] = self.failure_summary
        if self.http_status is not None:
            result["http_status"] = self.http_status
        if self.retry_after_seconds is not None:
            result["retry_after_seconds"] = self.retry_after_seconds
        return result


def build_operation_outcome(
    *,
    kind: OutcomeKind,
    reason_code: str,
    failure_summary: FailureSummary | None = None,
    error_type: str | None = None,
    failure_origin: str | None = None,
    failure_category: str | None = None,
    handling_policy: str | None = None,
    http_status: int | None = None,
    retry_after_seconds: float | None = None,
) -> OperationOutcome:
    """Build the canonical typed outcome payload."""
    if failure_summary is None:
        has_failure_context = any(
            value is not None
            for value in (
                error_type,
                failure_origin,
                failure_category,
                handling_policy,
            )
        )
        normalized_failure_summary = (
            build_failure_summary(
                error_type=error_type,
                failure_origin=failure_origin,
                failure_category=failure_category,
                handling_policy=handling_policy,
            )
            if has_failure_context
            else empty_failure_summary()
        )
    else:
        normalized_failure_summary = build_failure_summary(
            error_type=failure_summary.get("error_type"),
            failure_origin=failure_summary.get("failure_origin"),
            failure_category=failure_summary.get("failure_category"),
            handling_policy=failure_summary.get("handling_policy"),
        )
    return OperationOutcome(
        kind=kind,
        reason_code=reason_code,
        failure_summary=normalized_failure_summary,
        http_status=http_status,
        retry_after_seconds=retry_after_seconds,
    )


def build_operation_outcome_from_exception(
    err: BaseException,
    *,
    kind: OutcomeKind,
    reason_code: str,
    failure_origin: str,
    failure_category: str | None = None,
    handling_policy: str | None = None,
    http_status: int | None = None,
    retry_after_seconds: float | None = None,
) -> OperationOutcome:
    """Build one typed outcome from a concrete exception instance."""
    return OperationOutcome(
        kind=kind,
        reason_code=reason_code,
        failure_summary=build_failure_summary_from_exception(
            err,
            failure_origin=failure_origin,
            failure_category=failure_category,
            handling_policy=handling_policy,
        ),
        http_status=http_status,
        retry_after_seconds=retry_after_seconds,
    )


__all__ = [
    "FailureCategory",
    "FailureSummary",
    "HandlingPolicy",
    "OperationOutcome",
    "OperationOutcomePayload",
    "OutcomeKind",
    "TelemetryReadablePayload",
    "build_failure_summary",
    "build_failure_summary_from_exception",
    "build_operation_outcome",
    "build_operation_outcome_from_exception",
    "classify_failure_category",
    "empty_failure_summary",
    "extract_failure_summary",
    "handling_policy_for_category",
]
