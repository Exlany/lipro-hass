"""Tests for stable telemetry sink projections."""

from __future__ import annotations

from custom_components.lipro.core.telemetry import TelemetrySnapshot
from custom_components.lipro.core.telemetry.models import TelemetryJsonValue
from custom_components.lipro.core.telemetry.sinks import (
    CITelemetrySink,
    DeveloperTelemetrySink,
    DiagnosticsTelemetrySink,
    SystemHealthTelemetrySink,
)


def _as_mapping(value: TelemetryJsonValue) -> dict[str, TelemetryJsonValue]:
    assert isinstance(value, dict)
    return value


def _snapshot() -> TelemetrySnapshot:
    return TelemetrySnapshot(
        schema_version="telemetry.v1",
        report_id="report-1",
        generated_at=55.5,
        entry_ref="entry_deadbeef",
        protocol={
            "session": {
                "access_token_present": True,
                "refresh_token_present": False,
                "request_timeout": 30,
            },
            "telemetry": {"mqtt_last_error_type": "TimeoutError"},
            "auth_recovery": {
                "refresh_success_count": 2,
                "refresh_failure_count": 1,
            },
        },
        runtime={
            "device_count": 3,
            "polling_interval_seconds": 15,
            "last_update_success": True,
            "mqtt": {
                "connected": True,
                "disconnect_notified": False,
                "last_transport_error": "RuntimeError",
            },
            "command": {
                "trace_count": 2,
                "confirmation": {
                    "avg_latency_seconds": 1.5,
                    "timeout_total": 1,
                },
            },
            "tuning": {"metrics": {"avg_latency": 2.25}},
            "signals": {
                "connect_state_event_count": 1,
                "group_reconciliation_request_count": 2,
            },
        },
    )


def test_diagnostics_sink_keeps_full_snapshot_shape() -> None:
    view = DiagnosticsTelemetrySink().build_view(_snapshot())

    assert set(view) == {
        "schema_version",
        "report_id",
        "generated_at",
        "entry_ref",
        "failure_summary",
        "protocol",
        "runtime",
    }
    assert view["entry_ref"] == "entry_deadbeef"
    assert view["failure_summary"] == {
        "failure_category": "network",
        "failure_origin": "protocol.mqtt",
        "handling_policy": "retry",
        "error_type": "TimeoutError",
    }
    protocol = _as_mapping(view["protocol"])
    telemetry = _as_mapping(protocol["telemetry"])
    assert telemetry["mqtt_last_error_type"] == "TimeoutError"
    assert view["runtime"]["device_count"] == 3


def test_system_health_sink_reduces_to_summary_metrics() -> None:
    view = SystemHealthTelemetrySink().build_view(_snapshot())

    assert set(view) == {
        "schema_version",
        "report_id",
        "generated_at",
        "entry_ref",
        "failure_summary",
        "device_count",
        "polling_interval_seconds",
        "last_update_success",
        "mqtt_connected",
        "mqtt_disconnect_notified",
        "mqtt_last_transport_error",
        "command_trace_count",
        "command_confirmation_avg_latency_seconds",
        "command_confirmation_timeout_total",
        "connect_state_event_count",
        "group_reconciliation_request_count",
        "refresh_avg_latency_seconds",
        "protocol_mqtt_last_error_type",
        "auth_refresh_success_count",
        "auth_refresh_failure_count",
    }
    assert view["device_count"] == 3
    assert view["mqtt_connected"] is True
    assert view["command_trace_count"] == 2
    assert view["failure_summary"] == {
        "failure_category": "network",
        "failure_origin": "protocol.mqtt",
        "handling_policy": "retry",
        "error_type": "TimeoutError",
    }
    assert view["protocol_mqtt_last_error_type"] == "TimeoutError"
    assert view["command_confirmation_avg_latency_seconds"] == 1.5
    assert view["command_confirmation_timeout_total"] == 1
    assert view["refresh_avg_latency_seconds"] == 2.25
    assert view["auth_refresh_success_count"] == 2
    assert view["auth_refresh_failure_count"] == 1


def test_developer_and_ci_sinks_keep_stable_headers() -> None:
    developer = DeveloperTelemetrySink().build_view(_snapshot())
    ci = CITelemetrySink().build_view(_snapshot())

    assert set(developer) == {
        "schema_version",
        "report_id",
        "generated_at",
        "entry_ref",
        "failure_summary",
        "protocol",
        "runtime",
        "protocol_session_flags",
    }
    assert set(ci) == {
        "schema_version",
        "report_id",
        "generated_at",
        "entry_ref",
        "summary",
    }
    assert set(ci["summary"]) == {
        "device_count",
        "mqtt_connected",
        "command_trace_count",
        "connect_state_event_count",
        "command_confirmation_timeout_total",
        "refresh_avg_latency_seconds",
        "auth_refresh_success_count",
    }
    assert developer["report_id"] == "report-1"
    assert developer["protocol_session_flags"]["access_token_present"] is True
    assert ci["summary"]["device_count"] == 3
    assert ci["summary"]["command_confirmation_timeout_total"] == 1
    assert ci["summary"]["refresh_avg_latency_seconds"] == 2.25
    assert ci["summary"]["auth_refresh_success_count"] == 2
    assert ci["generated_at"] == 55.5
