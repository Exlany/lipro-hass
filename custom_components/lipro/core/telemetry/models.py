"""Formal telemetry contracts for exporter-owned assurance views."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from .json_payloads import (
    CardinalityBudget,
    TelemetrySensitivity,
    normalize_telemetry_key,
)
from .outcomes import (
    FailureCategory,
    FailureSummary,
    HandlingPolicy,
    OperationOutcome,
    OperationOutcomePayload,
    OutcomeKind,
    TelemetryReadablePayload,
    build_failure_summary,
    build_failure_summary_from_exception,
    build_operation_outcome,
    build_operation_outcome_from_exception,
    classify_failure_category,
    empty_failure_summary,
    extract_failure_summary,
    handling_policy_for_category,
)

SCHEMA_VERSION = "telemetry.v1"

type TelemetryJsonScalar = str | int | float | bool | None
type TelemetryJsonValue = (
    TelemetryJsonScalar | list[TelemetryJsonValue] | dict[str, TelemetryJsonValue]
)
type TelemetrySourcePayload = dict[str, TelemetryJsonValue]


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
    "TelemetryJsonValue",
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
