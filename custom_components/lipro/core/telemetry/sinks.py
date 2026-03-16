"""Stable telemetry sink projections."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .models import TelemetrySnapshot

type FailureSummary = dict[str, str | None]


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


def _header(snapshot: TelemetrySnapshot) -> dict[str, Any]:
    return {
        "schema_version": snapshot.schema_version,
        "report_id": snapshot.report_id,
        "generated_at": snapshot.generated_at,
        "entry_ref": snapshot.entry_ref,
    }


def _empty_failure_summary() -> FailureSummary:
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


def _classify_failure_category(error_type: str | None) -> str | None:
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


def _handling_policy_for_category(category: str | None) -> str | None:
    if category is None:
        return None
    return {
        "auth": "reauth",
        "network": "retry",
        "protocol": "inspect",
        "runtime": "inspect",
        "unexpected": "escalate",
    }.get(category)


def _extract_failure_summary(
    payload: Mapping[str, Any] | object,
    *,
    default_origin: str,
    raw_error_keys: tuple[str, ...],
) -> FailureSummary:
    if not isinstance(payload, Mapping):
        return _empty_failure_summary()

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

    failure_category = _coerce_text(
        summary_payload.get("failure_category")
    ) or _classify_failure_category(error_type)
    failure_origin = _coerce_text(summary_payload.get("failure_origin"))
    if failure_origin is None and (
        failure_category is not None or error_type is not None
    ):
        failure_origin = default_origin
    handling_policy = _coerce_text(
        summary_payload.get("handling_policy")
    ) or _handling_policy_for_category(failure_category)

    return {
        "failure_category": failure_category,
        "failure_origin": failure_origin,
        "handling_policy": handling_policy,
        "error_type": error_type,
    }


def _build_failure_summary(snapshot: TelemetrySnapshot) -> FailureSummary:
    protocol_telemetry = snapshot.protocol.get("telemetry")
    runtime_mqtt = snapshot.runtime.get("mqtt")

    for payload, origin, raw_error_keys in (
        (protocol_telemetry, "protocol.mqtt", ("mqtt_last_error_type",)),
        (runtime_mqtt, "runtime.mqtt", ("last_transport_error",)),
    ):
        summary = _extract_failure_summary(
            payload,
            default_origin=origin,
            raw_error_keys=raw_error_keys,
        )
        if summary["failure_category"] is not None or summary["error_type"] is not None:
            return summary
    return _empty_failure_summary()


class DiagnosticsTelemetrySink:
    """Diagnostics-oriented sink with full exporter truth."""

    name = "diagnostics"

    def build_view(self, snapshot: TelemetrySnapshot) -> Mapping[str, Any]:
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

    def build_view(self, snapshot: TelemetrySnapshot) -> Mapping[str, Any]:
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

    def build_view(self, snapshot: TelemetrySnapshot) -> Mapping[str, Any]:
        """Return the developer projection for one snapshot."""
        protocol_session = snapshot.protocol.get("session")
        return {
            **_header(snapshot),
            "failure_summary": _build_failure_summary(snapshot),
            "protocol": snapshot.protocol,
            "runtime": snapshot.runtime,
            "protocol_session_flags": (
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
            ),
        }


class CITelemetrySink:
    """CI-friendly sink with deterministic summary fields."""

    name = "ci"

    def build_view(self, snapshot: TelemetrySnapshot) -> Mapping[str, Any]:
        """Return the CI/replay projection for one snapshot."""
        system_health = SystemHealthTelemetrySink().build_view(snapshot)
        return {
            **_header(snapshot),
            "summary": {
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
            },
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
