"""Shared assertion helpers for protocol replay scenarios."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from custom_components.lipro.core.telemetry.exporter import RuntimeTelemetryExporter
from custom_components.lipro.core.telemetry.models import TelemetryViews
from tests.harness.protocol.replay_models import ReplayExecutionResult, ReplayManifest


class _ReplayProtocolSource:
    def __init__(self, snapshot: dict[str, Any]) -> None:
        self._snapshot = snapshot

    def get_protocol_telemetry_snapshot(self) -> dict[str, Any]:
        return dict(self._snapshot)


class _ReplayRuntimeSource:
    def __init__(self, snapshot: dict[str, Any]) -> None:
        self._snapshot = snapshot

    def get_runtime_telemetry_snapshot(self) -> dict[str, Any]:
        return dict(self._snapshot)


def assert_replay_canonical_contract(
    result: ReplayExecutionResult,
    *,
    expected_canonical: object,
    expected_fingerprint: str | None = None,
) -> None:
    """Assert one replay result resolves to the expected canonical contract."""
    assert result.error_category is None
    assert result.drift_flags == ()
    assert result.canonical == expected_canonical
    if expected_fingerprint is not None:
        assert result.fingerprint == expected_fingerprint


def assert_replay_has_no_drift(
    result: ReplayExecutionResult,
    *,
    expected_family: str,
    expected_version: str,
) -> None:
    """Assert one replay result does not report drift or execution failure."""
    assert result.manifest.family == expected_family
    assert result.manifest.version == expected_version
    assert result.error_category is None
    assert result.drift_flags == ()


def build_replay_exporter_views(
    manifest: ReplayManifest,
    result: ReplayExecutionResult,
) -> TelemetryViews:
    """Project replay telemetry through the formal exporter truth."""
    entry_id = f"replay-entry-{manifest.scenario_id}"
    generated_at = datetime.fromisoformat(manifest.controls.clock_baseline).timestamp()
    protocol_snapshot = {
        "entry_id": entry_id,
        "session": {
            "entry_id": entry_id,
            "access_token_present": manifest.channel == "rest",
            "refresh_token_present": True,
            "request_timeout": 30,
        },
        "telemetry": {
            "mqtt_last_error_type": result.error_category,
        },
        "auth_recovery": {
            "refresh_success_count": 1 if manifest.channel == "rest" else 0,
            "refresh_failure_count": 0 if result.error_category is None else 1,
            "last_refresh_outcome": (
                "success" if result.error_category is None else "failure"
            ),
        },
    }
    runtime_snapshot = {
        "entry_id": entry_id,
        "device_count": 1,
        "polling_interval_seconds": 15,
        "last_update_success": result.error_category is None,
        "mqtt": {
            "connected": manifest.channel == "mqtt",
            "disconnect_notified": False,
            "last_transport_error": result.error_category,
        },
        "command": {
            "trace_count": 1,
            "confirmation": {
                "avg_latency_seconds": 0.25,
                "timeout_total": 0,
            },
        },
        "tuning": {
            "metrics": {
                "avg_latency": 0.5,
            }
        },
        "signals": {
            "connect_state_event_count": 1 if manifest.channel == "mqtt" else 0,
            "group_reconciliation_request_count": 0,
        },
        "recent_command_traces": [
            {
                "device_serial": "03ab5ccd7c111111",
                "route": manifest.channel,
                "issued_at": result.finished_at,
            }
        ],
    }
    return RuntimeTelemetryExporter(
        protocol_source=_ReplayProtocolSource(protocol_snapshot),
        runtime_source=_ReplayRuntimeSource(runtime_snapshot),
        time_provider=lambda: generated_at,
        report_id_factory=lambda *_: f"replay-{manifest.scenario_id}",
    ).export_views()


def assert_exporter_backed_replay_telemetry(
    manifest: ReplayManifest,
    result: ReplayExecutionResult,
) -> TelemetryViews:
    """Assert replay telemetry is projected through the 07.3 exporter truth."""
    views = build_replay_exporter_views(manifest, result)
    diagnostics = views.diagnostics
    system_health = views.system_health
    trace = diagnostics["runtime"]["recent_command_traces"][0]

    assert diagnostics["schema_version"] == "telemetry.v1"
    assert system_health["refresh_avg_latency_seconds"] == 0.5
    assert system_health["command_confirmation_avg_latency_seconds"] == 0.25
    assert system_health["command_confirmation_timeout_total"] == 0
    assert system_health["auth_refresh_success_count"] == (
        1 if manifest.channel == "rest" else 0
    )
    assert system_health["mqtt_connected"] is (manifest.channel == "mqtt")
    assert "device_serial" not in trace
    assert "device_id" not in trace
    assert trace["device_ref"].startswith("device_")
    return views


__all__ = [
    "assert_exporter_backed_replay_telemetry",
    "assert_replay_canonical_contract",
    "assert_replay_has_no_drift",
    "build_replay_exporter_views",
]
