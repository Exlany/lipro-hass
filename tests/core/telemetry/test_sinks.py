"""Tests for stable telemetry sink projections."""

from __future__ import annotations

from custom_components.lipro.core.telemetry import TelemetrySnapshot
from custom_components.lipro.core.telemetry.sinks import (
    CITelemetrySink,
    DeveloperTelemetrySink,
    DiagnosticsTelemetrySink,
    SystemHealthTelemetrySink,
)


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

    assert view["entry_ref"] == "entry_deadbeef"
    assert view["protocol"]["telemetry"]["mqtt_last_error_type"] == "TimeoutError"
    assert view["runtime"]["device_count"] == 3


def test_system_health_sink_reduces_to_summary_metrics() -> None:
    view = SystemHealthTelemetrySink().build_view(_snapshot())

    assert view["device_count"] == 3
    assert view["mqtt_connected"] is True
    assert view["command_trace_count"] == 2
    assert view["protocol_mqtt_last_error_type"] == "TimeoutError"
    assert view["command_confirmation_avg_latency_seconds"] == 1.5
    assert view["command_confirmation_timeout_total"] == 1
    assert view["refresh_avg_latency_seconds"] == 2.25
    assert view["auth_refresh_success_count"] == 2
    assert view["auth_refresh_failure_count"] == 1


def test_developer_and_ci_sinks_keep_stable_headers() -> None:
    developer = DeveloperTelemetrySink().build_view(_snapshot())
    ci = CITelemetrySink().build_view(_snapshot())

    assert developer["report_id"] == "report-1"
    assert developer["protocol_session_flags"]["access_token_present"] is True
    assert ci["summary"]["device_count"] == 3
    assert ci["summary"]["command_confirmation_timeout_total"] == 1
    assert ci["summary"]["refresh_avg_latency_seconds"] == 2.25
    assert ci["summary"]["auth_refresh_success_count"] == 2
    assert ci["generated_at"] == 55.5
