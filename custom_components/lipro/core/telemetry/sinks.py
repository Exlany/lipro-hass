"""Stable telemetry sink projections."""

from __future__ import annotations

from .models import (
    CITelemetrySummary,
    CITelemetryView,
    DeveloperTelemetryView,
    DiagnosticsTelemetryView,
    FailureSummary,
    ProtocolSessionFlags,
    SystemHealthTelemetryView,
    TelemetryHeaderPayload,
    TelemetrySnapshot,
    empty_failure_summary,
    extract_failure_summary,
)


def _header(snapshot: TelemetrySnapshot) -> TelemetryHeaderPayload:
    return {
        "schema_version": snapshot.schema_version,
        "report_id": snapshot.report_id,
        "generated_at": snapshot.generated_at,
        "entry_ref": snapshot.entry_ref,
    }


def _build_failure_summary(snapshot: TelemetrySnapshot) -> FailureSummary:
    protocol_telemetry = snapshot.protocol.get("telemetry")
    runtime_mqtt = snapshot.runtime.get("mqtt")

    for payload, origin, raw_error_keys in (
        (snapshot.runtime, "runtime.update", ()),
        (protocol_telemetry, "protocol.mqtt", ("mqtt_last_error_type",)),
        (runtime_mqtt, "runtime.mqtt", ("last_transport_error",)),
    ):
        summary = extract_failure_summary(
            payload,
            default_origin=origin,
            raw_error_keys=raw_error_keys,
        )
        if summary["failure_category"] is not None or summary["error_type"] is not None:
            return summary
    return empty_failure_summary()


class DiagnosticsTelemetrySink:
    """Diagnostics-oriented sink with full exporter truth."""

    name = "diagnostics"

    def build_view(self, snapshot: TelemetrySnapshot) -> DiagnosticsTelemetryView:
        """Return the diagnostics projection for one snapshot."""
        return {
            **_header(snapshot),
            "failure_summary": _build_failure_summary(snapshot),
            "protocol": snapshot.protocol,
            "runtime": snapshot.runtime,
        }


class SystemHealthTelemetrySink:
    """System-health sink with coarse-grained summary metrics."""

    name = "system_health"

    def build_view(self, snapshot: TelemetrySnapshot) -> SystemHealthTelemetryView:
        """Return the system-health projection for one snapshot."""
        runtime_mqtt = snapshot.runtime.get("mqtt")
        runtime_signals = snapshot.runtime.get("signals")
        runtime_command = snapshot.runtime.get("command")
        runtime_tuning = snapshot.runtime.get("tuning")
        protocol_telemetry = snapshot.protocol.get("telemetry")
        protocol_auth_recovery = snapshot.protocol.get("auth_recovery")
        command_confirmation = (
            runtime_command.get("confirmation")
            if isinstance(runtime_command, dict)
            else None
        )
        tuning_metrics = (
            runtime_tuning.get("metrics") if isinstance(runtime_tuning, dict) else None
        )
        return {
            **_header(snapshot),
            "failure_summary": _build_failure_summary(snapshot),
            "device_count": snapshot.runtime.get("device_count", 0),
            "polling_interval_seconds": snapshot.runtime.get(
                "polling_interval_seconds"
            ),
            "last_update_success": snapshot.runtime.get("last_update_success"),
            "mqtt_connected": (
                runtime_mqtt.get("connected")
                if isinstance(runtime_mqtt, dict)
                else None
            ),
            "mqtt_disconnect_notified": (
                runtime_mqtt.get("disconnect_notified")
                if isinstance(runtime_mqtt, dict)
                else None
            ),
            "mqtt_last_transport_error": (
                runtime_mqtt.get("last_transport_error")
                if isinstance(runtime_mqtt, dict)
                else None
            ),
            "command_trace_count": (
                runtime_command.get("trace_count")
                if isinstance(runtime_command, dict)
                else 0
            ),
            "command_confirmation_avg_latency_seconds": (
                command_confirmation.get("avg_latency_seconds")
                if isinstance(command_confirmation, dict)
                else None
            ),
            "command_confirmation_timeout_total": (
                command_confirmation.get("timeout_total")
                if isinstance(command_confirmation, dict)
                else 0
            ),
            "connect_state_event_count": (
                runtime_signals.get("connect_state_event_count")
                if isinstance(runtime_signals, dict)
                else 0
            ),
            "group_reconciliation_request_count": (
                runtime_signals.get("group_reconciliation_request_count")
                if isinstance(runtime_signals, dict)
                else 0
            ),
            "refresh_avg_latency_seconds": (
                tuning_metrics.get("avg_latency")
                if isinstance(tuning_metrics, dict)
                else None
            ),
            "protocol_mqtt_last_error_type": (
                protocol_telemetry.get("mqtt_last_error_type")
                if isinstance(protocol_telemetry, dict)
                else None
            ),
            "auth_refresh_success_count": (
                protocol_auth_recovery.get("refresh_success_count")
                if isinstance(protocol_auth_recovery, dict)
                else 0
            ),
            "auth_refresh_failure_count": (
                protocol_auth_recovery.get("refresh_failure_count")
                if isinstance(protocol_auth_recovery, dict)
                else 0
            ),
        }


class DeveloperTelemetrySink:
    """Developer-facing sink with richer but still normalized detail."""

    name = "developer"

    def build_view(self, snapshot: TelemetrySnapshot) -> DeveloperTelemetryView:
        """Return the developer projection for one snapshot."""
        protocol_session = snapshot.protocol.get("session")
        protocol_session_flags: ProtocolSessionFlags = (
            {
                key: protocol_session.get(key)
                for key in (
                    "access_token_present",
                    "refresh_token_present",
                    "request_timeout",
                )
                if key in protocol_session
            }
            if isinstance(protocol_session, dict)
            else {}
        )
        return {
            **_header(snapshot),
            "failure_summary": _build_failure_summary(snapshot),
            "protocol": snapshot.protocol,
            "runtime": snapshot.runtime,
            "protocol_session_flags": protocol_session_flags,
        }


class CITelemetrySink:
    """CI-friendly sink with deterministic summary fields."""

    name = "ci"

    def build_view(self, snapshot: TelemetrySnapshot) -> CITelemetryView:
        """Return the CI/replay projection for one snapshot."""
        system_health = SystemHealthTelemetrySink().build_view(snapshot)
        summary: CITelemetrySummary = {
            "device_count": system_health.get("device_count", 0),
            "mqtt_connected": system_health.get("mqtt_connected"),
            "command_trace_count": system_health.get("command_trace_count", 0),
            "connect_state_event_count": system_health.get(
                "connect_state_event_count", 0
            ),
            "command_confirmation_timeout_total": system_health.get(
                "command_confirmation_timeout_total", 0
            ),
            "refresh_avg_latency_seconds": system_health.get(
                "refresh_avg_latency_seconds"
            ),
            "auth_refresh_success_count": system_health.get(
                "auth_refresh_success_count", 0
            ),
        }
        return {
            **_header(snapshot),
            "summary": summary,
        }


DEFAULT_TELEMETRY_SINKS = (
    DiagnosticsTelemetrySink(),
    SystemHealthTelemetrySink(),
    DeveloperTelemetrySink(),
    CITelemetrySink(),
)

__all__ = [
    "DEFAULT_TELEMETRY_SINKS",
    "CITelemetrySink",
    "DeveloperTelemetrySink",
    "DiagnosticsTelemetrySink",
    "SystemHealthTelemetrySink",
]
