"""Formal telemetry contracts for exporter-owned assurance views."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal, NotRequired, TypedDict

SCHEMA_VERSION = "telemetry.v1"

type FailureCategory = Literal["auth", "network", "protocol", "runtime", "unexpected"]
type HandlingPolicy = Literal["reauth", "retry", "inspect", "escalate"]
type OutcomeKind = Literal["success", "skipped", "degraded", "failed"]
type TelemetryJsonScalar = str | int | float | bool | None
type TelemetryJsonValue = (
    TelemetryJsonScalar
    | list[TelemetryJsonValue]
    | dict[str, TelemetryJsonValue]
)
type TelemetryReadablePayload = Mapping[str, object]
type TelemetrySourcePayload = dict[str, TelemetryJsonValue]


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


class TelemetryHeaderPayload(TypedDict):
    """Shared header fields emitted by every telemetry sink."""

    schema_version: str
    report_id: str
    generated_at: float
    entry_ref: str | None


class TelemetrySnapshotPayload(TypedDict):
    """JSON-safe exporter snapshot payload."""

    schema_version: str
    report_id: str
    generated_at: float
    entry_ref: str | None
    protocol: TelemetrySourcePayload
    runtime: TelemetrySourcePayload


class DiagnosticsTelemetryView(TelemetryHeaderPayload):
    """Diagnostics sink payload with full protocol/runtime detail."""

    failure_summary: FailureSummary
    protocol: TelemetrySourcePayload
    runtime: TelemetrySourcePayload


class SystemHealthTelemetryView(TelemetryHeaderPayload):
    """System-health sink payload with summary metrics."""

    failure_summary: FailureSummary
    device_count: int
    polling_interval_seconds: int | float | None
    last_update_success: bool | None
    mqtt_connected: bool | None
    mqtt_disconnect_notified: bool | None
    mqtt_last_transport_error: str | None
    command_trace_count: int
    command_confirmation_avg_latency_seconds: int | float | None
    command_confirmation_timeout_total: int
    connect_state_event_count: int
    group_reconciliation_request_count: int
    refresh_avg_latency_seconds: int | float | None
    protocol_mqtt_last_error_type: str | None
    auth_refresh_success_count: int
    auth_refresh_failure_count: int


class ProtocolSessionFlags(TypedDict, total=False):
    """Subset of session flags safe to expose to developer tooling."""

    access_token_present: bool
    refresh_token_present: bool
    request_timeout: int | float | None


class DeveloperTelemetryView(TelemetryHeaderPayload):
    """Developer sink payload with normalized detail and flags."""

    failure_summary: FailureSummary
    protocol: TelemetrySourcePayload
    runtime: TelemetrySourcePayload
    protocol_session_flags: ProtocolSessionFlags


class CITelemetrySummary(TypedDict):
    """Stable CI/replay summary metrics."""

    device_count: int
    mqtt_connected: bool | None
    command_trace_count: int
    connect_state_event_count: int
    command_confirmation_timeout_total: int
    refresh_avg_latency_seconds: int | float | None
    auth_refresh_success_count: int


class CITelemetryView(TelemetryHeaderPayload):
    """CI sink payload with deterministic summary-only content."""

    summary: CITelemetrySummary


class TelemetryViewsPayload(TypedDict):
    """Stable mapping form bundling all sink projections."""

    snapshot: TelemetrySnapshotPayload
    diagnostics: DiagnosticsTelemetryView
    system_health: SystemHealthTelemetryView
    developer: DeveloperTelemetryView
    ci: CITelemetryView

_BLOCKED_KEYS = frozenset(
    {
        "access_token",
        "accesskey",
        "biz_id",
        "bizid",
        "device_id",
        "deviceid",
        "gatewaydeviceid",
        "gateway_device_id",
        "password",
        "passwordhash",
        "password_hash",
        "phone",
        "phone_id",
        "phoneid",
        "refresh_access_key",
        "refresh_token",
        "refreshaccesskey",
        "refreshtoken",
        "secret",
        "secret_key",
        "secretkey",
        "serial",
        "user_id",
        "userid",
    }
)

_REFERENCE_ALIASES = {
    "device_id": "device_ref",
    "deviceid": "device_ref",
    "device_name": "device_ref",
    "devicename": "device_ref",
    "device_serial": "device_ref",
    "deviceserial": "device_ref",
    "entry_id": "entry_ref",
    "entryid": "entry_ref",
    "gateway_device_id": "device_ref",
    "gatewaydeviceid": "device_ref",
    "group_id": "device_ref",
    "groupid": "device_ref",
    "serial": "device_ref",
}

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


def normalize_telemetry_key(key: str) -> str:
    """Normalize one telemetry field name for policy lookup."""
    return key.lower().replace("-", "_")


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
        normalized_failure_summary = failure_summary
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


@dataclass(frozen=True, slots=True)
class TelemetrySensitivity:
    """Sensitivity contract used by the exporter."""

    blocked_keys: frozenset[str] = field(default_factory=lambda: _BLOCKED_KEYS)
    reference_aliases: dict[str, str] = field(
        default_factory=lambda: dict(_REFERENCE_ALIASES)
    )

    def is_blocked(self, key: str) -> bool:
        """Return whether a field must be removed from exported views."""
        normalized = normalize_telemetry_key(key)
        if normalized in self.reference_aliases:
            return False
        return normalized in self.blocked_keys

    def reference_alias_for(self, key: str) -> str | None:
        """Return the pseudonymous alias for a field, when configured."""
        normalized = normalize_telemetry_key(key)
        return self.reference_aliases.get(normalized)


@dataclass(frozen=True, slots=True)
class CardinalityBudget:
    """Budget contract preventing high-cardinality telemetry growth."""

    max_mapping_items: int = 32
    max_sequence_items: int = 20
    max_string_length: int = 256


@dataclass(frozen=True, slots=True)
class TelemetrySnapshot:
    """Normalized exporter snapshot shared by all sinks."""

    schema_version: str
    report_id: str
    generated_at: float
    entry_ref: str | None
    protocol: TelemetrySourcePayload
    runtime: TelemetrySourcePayload

    def to_dict(self) -> TelemetrySnapshotPayload:
        """Return a JSON-friendly representation of the snapshot."""
        return {
            "schema_version": self.schema_version,
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "entry_ref": self.entry_ref,
            "protocol": self.protocol,
            "runtime": self.runtime,
        }


@dataclass(frozen=True, slots=True)
class TelemetryViews:
    """Exporter projections for diagnostics/system-health/developer/CI."""

    snapshot: TelemetrySnapshot
    diagnostics: DiagnosticsTelemetryView
    system_health: SystemHealthTelemetryView
    developer: DeveloperTelemetryView
    ci: CITelemetryView

    def to_dict(self) -> TelemetryViewsPayload:
        """Return all sink views in a stable dictionary shape."""
        return {
            "snapshot": self.snapshot.to_dict(),
            "diagnostics": self.diagnostics,
            "system_health": self.system_health,
            "developer": self.developer,
            "ci": self.ci,
        }


type TelemetrySinkPayload = (
    DiagnosticsTelemetryView
    | SystemHealthTelemetryView
    | DeveloperTelemetryView
    | CITelemetryView
)


__all__ = [
    "SCHEMA_VERSION",
    "CITelemetrySummary",
    "CITelemetryView",
    "CardinalityBudget",
    "DeveloperTelemetryView",
    "DiagnosticsTelemetryView",
    "FailureCategory",
    "FailureSummary",
    "HandlingPolicy",
    "OperationOutcome",
    "OperationOutcomePayload",
    "OutcomeKind",
    "ProtocolSessionFlags",
    "SystemHealthTelemetryView",
    "TelemetryHeaderPayload",
    "TelemetryReadablePayload",
    "TelemetrySensitivity",
    "TelemetrySinkPayload",
    "TelemetrySnapshot",
    "TelemetrySnapshotPayload",
    "TelemetrySourcePayload",
    "TelemetryViews",
    "TelemetryViewsPayload",
    "build_failure_summary",
    "build_failure_summary_from_exception",
    "build_operation_outcome",
    "build_operation_outcome_from_exception",
    "classify_failure_category",
    "empty_failure_summary",
    "extract_failure_summary",
    "handling_policy_for_category",
    "normalize_telemetry_key",
]
