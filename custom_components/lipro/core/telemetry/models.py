"""Formal telemetry contracts for exporter-owned assurance views."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

SCHEMA_VERSION = "telemetry.v1"

type FailureCategory = Literal["auth", "network", "protocol", "runtime", "unexpected"]
type HandlingPolicy = Literal["reauth", "retry", "inspect", "escalate"]
type FailureSummary = dict[str, str | None]

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


def handling_policy_for_category(category: str | None) -> HandlingPolicy | None:
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


def build_failure_summary(
    *,
    error_type: str | None,
    failure_origin: str | None,
    failure_category: str | None = None,
    handling_policy: str | None = None,
) -> FailureSummary:
    """Build the canonical failure-summary payload."""
    normalized_category = failure_category or classify_failure_category(error_type)
    normalized_policy = handling_policy or handling_policy_for_category(
        normalized_category
    )
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
    payload: Mapping[str, Any] | object,
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
    protocol: dict[str, Any]
    runtime: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
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
    diagnostics: dict[str, Any]
    system_health: dict[str, Any]
    developer: dict[str, Any]
    ci: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return all sink views in a stable dictionary shape."""
        return {
            "snapshot": self.snapshot.to_dict(),
            "diagnostics": self.diagnostics,
            "system_health": self.system_health,
            "developer": self.developer,
            "ci": self.ci,
        }


__all__ = [
    "SCHEMA_VERSION",
    "CardinalityBudget",
    "FailureCategory",
    "FailureSummary",
    "HandlingPolicy",
    "TelemetrySensitivity",
    "TelemetrySnapshot",
    "TelemetryViews",
    "build_failure_summary",
    "build_failure_summary_from_exception",
    "classify_failure_category",
    "empty_failure_summary",
    "extract_failure_summary",
    "handling_policy_for_category",
    "normalize_telemetry_key",
]
