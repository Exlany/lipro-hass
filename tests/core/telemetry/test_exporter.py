"""Tests for the pull-first runtime telemetry exporter."""

from __future__ import annotations

from custom_components.lipro.core.telemetry import CardinalityBudget
from custom_components.lipro.core.telemetry.exporter import RuntimeTelemetryExporter
from custom_components.lipro.core.telemetry.models import (
    TelemetryJsonValue,
    TelemetrySourcePayload,
)


def _as_mapping(value: TelemetryJsonValue) -> dict[str, TelemetryJsonValue]:
    assert isinstance(value, dict)
    return value


def _as_list(value: TelemetryJsonValue) -> list[TelemetryJsonValue]:
    assert isinstance(value, list)
    return value


def _as_str(value: TelemetryJsonValue) -> str:
    assert isinstance(value, str)
    return value


class _ProtocolSource:
    def get_protocol_telemetry_snapshot(self) -> TelemetrySourcePayload:
        return {
            "entry_id": "entry-1",
            "session": {
                "entry_id": "entry-1",
                "phone_id": "13800000000",
                "access_token_present": True,
                "refresh_token_present": True,
            },
            "telemetry": {
                "mqtt_start_count": 1,
                "mqtt_last_error_type": "RuntimeError",
            },
        }


class _RuntimeSource:
    def get_runtime_telemetry_snapshot(self) -> TelemetrySourcePayload:
        return {
            "entry_id": "entry-1",
            "device_count": 3,
            "polling_interval_seconds": 15,
            "last_update_success": True,
            "mqtt": {
                "connected": True,
                "device_id": "03ab5ccd7c123456",
                "last_transport_error": "TimeoutError",
            },
            "command": {"trace_count": 1},
            "signals": {
                "connect_state_event_count": 12,
                "recent_connect_state_events": [
                    {
                        "device_serial": f"03ab5ccd7c{i:06d}",
                        "timestamp": float(i),
                        "is_online": True,
                    }
                    for i in range(12)
                ],
            },
            "recent_command_traces": [
                {
                    "device_id": "03ab5ccd7c999999",
                    "route": "mqtt",
                    "password_hash": "x",
                }
            ],
        }


class _RuntimeOnlyEntrySource:
    def get_runtime_telemetry_snapshot(self) -> TelemetrySourcePayload:
        return {
            "entry_id": "entry-runtime-only",
            "message": "x" * 128,
            "nested": {
                "refresh_token": "secret",
                "device_id": "03ab5ccd7c654321",
                "notes": "y" * 128,
            },
        }


def test_exporter_redacts_sensitive_fields_and_pseudonymizes_ids() -> None:
    exporter = RuntimeTelemetryExporter(
        protocol_source=_ProtocolSource(),
        runtime_source=_RuntimeSource(),
        cardinality_budget=CardinalityBudget(max_sequence_items=10),
        report_id_factory=lambda *_: "report-a",
    )

    snapshot = exporter.export_snapshot()
    protocol_session = _as_mapping(snapshot.protocol["session"])
    runtime_mqtt = _as_mapping(snapshot.runtime["mqtt"])
    recent_command_traces = _as_list(snapshot.runtime["recent_command_traces"])
    recent_trace = _as_mapping(recent_command_traces[0])
    runtime_signals = _as_mapping(snapshot.runtime["signals"])
    recent_events = _as_list(runtime_signals["recent_connect_state_events"])

    assert snapshot.schema_version == "telemetry.v1"
    assert snapshot.report_id == "report-a"
    assert snapshot.entry_ref is not None
    assert protocol_session["access_token_present"] is True
    assert "phone_id" not in protocol_session
    assert _as_str(runtime_mqtt["device_ref"]).startswith("device_")
    assert "device_id" not in runtime_mqtt
    assert "password_hash" not in recent_trace
    assert len(recent_events) == 10


def test_exporter_builds_stable_views_from_one_snapshot() -> None:
    exporter = RuntimeTelemetryExporter(
        protocol_source=_ProtocolSource(),
        runtime_source=_RuntimeSource(),
        report_id_factory=lambda *_: "report-b",
    )

    views = exporter.export_views()
    developer_entry_ref = views.developer["entry_ref"]
    ci_summary = views.ci["summary"]

    assert views.snapshot.schema_version == "telemetry.v1"
    assert views.diagnostics["schema_version"] == "telemetry.v1"
    assert views.system_health["device_count"] == 3
    assert views.system_health["mqtt_connected"] is True
    assert views.system_health["command_trace_count"] == 1
    assert isinstance(developer_entry_ref, str)
    assert developer_entry_ref.startswith("entry_")
    assert ci_summary["connect_state_event_count"] == 12


def test_exporter_falls_back_when_report_id_factory_rejects_length_argument() -> None:
    def _factory_without_length() -> str:
        return "report-no-arg"

    exporter = RuntimeTelemetryExporter(
        protocol_source=_ProtocolSource(),
        runtime_source=_RuntimeSource(),
        report_id_factory=_factory_without_length,
    )

    snapshot = exporter.export_snapshot()

    assert snapshot.report_id == "report-no-arg"


def test_exporter_uses_runtime_entry_id_when_protocol_entry_id_is_missing() -> None:
    class _ProtocolWithoutEntry:
        def get_protocol_telemetry_snapshot(self) -> TelemetrySourcePayload:
            return {"session": {"access_token_present": True}}

    exporter = RuntimeTelemetryExporter(
        protocol_source=_ProtocolWithoutEntry(),
        runtime_source=_RuntimeOnlyEntrySource(),
        cardinality_budget=CardinalityBudget(max_string_length=24),
        report_id_factory=lambda *_: "report-c",
    )

    snapshot = exporter.export_snapshot()
    nested = _as_mapping(snapshot.runtime["nested"])

    assert snapshot.entry_ref is not None
    assert _as_str(nested["device_ref"]).startswith("device_")
    assert "refresh_token" not in nested
    assert snapshot.runtime["message"] == "x" * 24
    assert nested["notes"] == "y" * 24
