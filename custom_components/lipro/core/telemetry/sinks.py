"""Stable telemetry sink projections."""

from __future__ import annotations

from typing import cast

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


def _mapping_child(
    value: dict[str, TelemetryJsonValue] | None,
    key: str,
) -> dict[str, TelemetryJsonValue] | None:
    if value is None:
        return None
    return _as_mapping(value.get(key))


def _get_int(value: TelemetryJsonValue, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    return default


def _mapping_get_int(
    value: dict[str, TelemetryJsonValue] | None,
    key: str,
    default: int = 0,
) -> int:
    if value is None:
        return default
    return _get_int(value.get(key), default)


def _get_number(value: TelemetryJsonValue) -> int | float | None:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return value
    return None


def _mapping_get_number(
    value: dict[str, TelemetryJsonValue] | None,
    key: str,
) -> int | float | None:
    if value is None:
        return None
    return _get_number(value.get(key))


def _get_bool(value: TelemetryJsonValue) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _mapping_get_bool(
    value: dict[str, TelemetryJsonValue] | None,
    key: str,
) -> bool | None:
    if value is None:
        return None
    return _get_bool(value.get(key))


def _get_str(value: TelemetryJsonValue) -> str | None:
    if isinstance(value, str):
        return value
    return None


def _mapping_get_str(
    value: dict[str, TelemetryJsonValue] | None,
    key: str,
) -> str | None:
    if value is None:
        return None
    return _get_str(value.get(key))


def _build_protocol_session_flags(snapshot: TelemetrySnapshot) -> ProtocolSessionFlags:
    protocol_session = _as_mapping(snapshot.protocol.get("session"))
    protocol_session_flags: ProtocolSessionFlags = {}
    if protocol_session is None:
        return protocol_session_flags

    access_token_present = _mapping_get_bool(protocol_session, "access_token_present")
    refresh_token_present = _mapping_get_bool(protocol_session, "refresh_token_present")
    request_timeout = _mapping_get_number(protocol_session, "request_timeout")

    if access_token_present is not None:
        protocol_session_flags["access_token_present"] = access_token_present
    if refresh_token_present is not None:
        protocol_session_flags["refresh_token_present"] = refresh_token_present
    if request_timeout is not None:
        protocol_session_flags["request_timeout"] = request_timeout
    return protocol_session_flags


def _build_system_health_runtime_payload(
    snapshot: TelemetrySnapshot,
) -> dict[str, TelemetryJsonValue]:
    runtime_mqtt = _as_mapping(snapshot.runtime.get("mqtt"))
    runtime_signals = _as_mapping(snapshot.runtime.get("signals"))
    runtime_command = _as_mapping(snapshot.runtime.get("command"))
    runtime_tuning = _as_mapping(snapshot.runtime.get("tuning"))
    command_confirmation = _mapping_child(runtime_command, "confirmation")
    tuning_metrics = _mapping_child(runtime_tuning, "metrics")

    return {
        "device_count": _mapping_get_int(snapshot.runtime, "device_count"),
        "polling_interval_seconds": _mapping_get_number(
            snapshot.runtime,
            "polling_interval_seconds",
        ),
        "last_update_success": _mapping_get_bool(
            snapshot.runtime,
            "last_update_success",
        ),
        "mqtt_connected": _mapping_get_bool(runtime_mqtt, "connected"),
        "mqtt_disconnect_notified": _mapping_get_bool(
            runtime_mqtt,
            "disconnect_notified",
        ),
        "mqtt_last_transport_error": _mapping_get_str(
            runtime_mqtt,
            "last_transport_error",
        ),
        "command_trace_count": _mapping_get_int(runtime_command, "trace_count"),
        "command_confirmation_avg_latency_seconds": _mapping_get_number(
            command_confirmation,
            "avg_latency_seconds",
        ),
        "command_confirmation_timeout_total": _mapping_get_int(
            command_confirmation,
            "timeout_total",
        ),
        "connect_state_event_count": _mapping_get_int(
            runtime_signals,
            "connect_state_event_count",
        ),
        "group_reconciliation_request_count": _mapping_get_int(
            runtime_signals,
            "group_reconciliation_request_count",
        ),
        "refresh_avg_latency_seconds": _mapping_get_number(
            tuning_metrics,
            "avg_latency",
        ),
    }


def _build_system_health_protocol_payload(
    snapshot: TelemetrySnapshot,
) -> dict[str, TelemetryJsonValue]:
    protocol_telemetry = _as_mapping(snapshot.protocol.get("telemetry"))
    protocol_auth_recovery = _as_mapping(snapshot.protocol.get("auth_recovery"))

    return {
        "protocol_mqtt_last_error_type": _mapping_get_str(
            protocol_telemetry,
            "mqtt_last_error_type",
        ),
        "auth_refresh_success_count": _mapping_get_int(
            protocol_auth_recovery,
            "refresh_success_count",
        ),
        "auth_refresh_failure_count": _mapping_get_int(
            protocol_auth_recovery,
            "refresh_failure_count",
        ),
    }


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
        return cast(
            SystemHealthTelemetryView,
            {
                **_header(snapshot),
                "failure_summary": _build_failure_summary(snapshot),
                **_build_system_health_runtime_payload(snapshot),
                **_build_system_health_protocol_payload(snapshot),
            },
        )


class DeveloperTelemetrySink:
    """Developer-facing sink with richer but still normalized detail."""

    name = "developer"

    def build_view(self, snapshot: TelemetrySnapshot) -> DeveloperTelemetryView:
        """Return the developer projection for one snapshot."""
        return {
            **_header(snapshot),
            "failure_summary": _build_failure_summary(snapshot),
            "protocol": snapshot.protocol,
            "runtime": snapshot.runtime,
            "protocol_session_flags": _build_protocol_session_flags(snapshot),
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
            "command_confirmation_timeout_total": system_health[
                "command_confirmation_timeout_total"
            ],
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
