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
    TelemetryJsonValue,
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


def _as_mapping(value: TelemetryJsonValue) -> dict[str, TelemetryJsonValue] | None:
    if isinstance(value, dict):
        return value
    return None


def _get_int(value: TelemetryJsonValue, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    return default


def _get_number(value: TelemetryJsonValue) -> int | float | None:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return value
    return None


def _get_bool(value: TelemetryJsonValue) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _get_str(value: TelemetryJsonValue) -> str | None:
    if isinstance(value, str):
        return value
    return None


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
        runtime_mqtt = _as_mapping(snapshot.runtime.get("mqtt"))
        runtime_signals = _as_mapping(snapshot.runtime.get("signals"))
        runtime_command = _as_mapping(snapshot.runtime.get("command"))
        runtime_tuning = _as_mapping(snapshot.runtime.get("tuning"))
        protocol_telemetry = _as_mapping(snapshot.protocol.get("telemetry"))
        protocol_auth_recovery = _as_mapping(snapshot.protocol.get("auth_recovery"))
        command_confirmation = (
            _as_mapping(runtime_command.get("confirmation"))
            if runtime_command is not None
            else None
        )
        tuning_metrics = (
            _as_mapping(runtime_tuning.get("metrics"))
            if runtime_tuning is not None
            else None
        )
        return {
            **_header(snapshot),
            "failure_summary": _build_failure_summary(snapshot),
            "device_count": _get_int(snapshot.runtime.get("device_count"), 0),
            "polling_interval_seconds": _get_number(
                snapshot.runtime.get("polling_interval_seconds")
            ),
            "last_update_success": _get_bool(
                snapshot.runtime.get("last_update_success")
            ),
            "mqtt_connected": (
                _get_bool(runtime_mqtt.get("connected"))
                if runtime_mqtt is not None
                else None
            ),
            "mqtt_disconnect_notified": (
                _get_bool(runtime_mqtt.get("disconnect_notified"))
                if runtime_mqtt is not None
                else None
            ),
            "mqtt_last_transport_error": (
                _get_str(runtime_mqtt.get("last_transport_error"))
                if runtime_mqtt is not None
                else None
            ),
            "command_trace_count": (
                _get_int(runtime_command.get("trace_count"), 0)
                if runtime_command is not None
                else 0
            ),
            "command_confirmation_avg_latency_seconds": (
                _get_number(command_confirmation.get("avg_latency_seconds"))
                if command_confirmation is not None
                else None
            ),
            "command_confirmation_timeout_total": (
                _get_int(command_confirmation.get("timeout_total"), 0)
                if command_confirmation is not None
                else 0
            ),
            "connect_state_event_count": (
                _get_int(runtime_signals.get("connect_state_event_count"), 0)
                if runtime_signals is not None
                else 0
            ),
            "group_reconciliation_request_count": (
                _get_int(runtime_signals.get("group_reconciliation_request_count"), 0)
                if runtime_signals is not None
                else 0
            ),
            "refresh_avg_latency_seconds": (
                _get_number(tuning_metrics.get("avg_latency"))
                if tuning_metrics is not None
                else None
            ),
            "protocol_mqtt_last_error_type": (
                _get_str(protocol_telemetry.get("mqtt_last_error_type"))
                if protocol_telemetry is not None
                else None
            ),
            "auth_refresh_success_count": (
                _get_int(protocol_auth_recovery.get("refresh_success_count"), 0)
                if protocol_auth_recovery is not None
                else 0
            ),
            "auth_refresh_failure_count": (
                _get_int(protocol_auth_recovery.get("refresh_failure_count"), 0)
                if protocol_auth_recovery is not None
                else 0
            ),
        }


class DeveloperTelemetrySink:
    """Developer-facing sink with richer but still normalized detail."""

    name = "developer"

    def build_view(self, snapshot: TelemetrySnapshot) -> DeveloperTelemetryView:
        """Return the developer projection for one snapshot."""
        protocol_session = _as_mapping(snapshot.protocol.get("session"))
        protocol_session_flags: ProtocolSessionFlags = {}
        if protocol_session is not None:
            access_token_present = _get_bool(protocol_session.get("access_token_present"))
            refresh_token_present = _get_bool(protocol_session.get("refresh_token_present"))
            request_timeout = _get_number(protocol_session.get("request_timeout"))
            if access_token_present is not None:
                protocol_session_flags["access_token_present"] = access_token_present
            if refresh_token_present is not None:
                protocol_session_flags["refresh_token_present"] = refresh_token_present
            if request_timeout is not None:
                protocol_session_flags["request_timeout"] = request_timeout
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
            "device_count": system_health["device_count"],
            "mqtt_connected": system_health["mqtt_connected"],
            "command_trace_count": system_health["command_trace_count"],
            "connect_state_event_count": system_health["connect_state_event_count"],
            "command_confirmation_timeout_total": system_health["command_confirmation_timeout_total"],
            "refresh_avg_latency_seconds": system_health["refresh_avg_latency_seconds"],
            "auth_refresh_success_count": system_health["auth_refresh_success_count"],
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
