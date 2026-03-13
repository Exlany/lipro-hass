"""Structured replay-run summary builders for assurance evidence."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from custom_components.lipro.core.telemetry.models import TelemetryViews
from tests.harness.protocol.replay_models import ReplayExecutionResult

_SCHEMA_VERSION = "replay.report.v1"


def _scenario_result(result: ReplayExecutionResult) -> str:
    if result.error_category is not None or result.drift_flags:
        return "failed"
    return "passed"


def build_replay_scenario_summary(
    result: ReplayExecutionResult,
    *,
    telemetry_views: TelemetryViews,
) -> dict[str, Any]:
    """Build one replay scenario summary row."""
    trace = telemetry_views.diagnostics["runtime"]["recent_command_traces"][0]
    return {
        "scenario_id": result.manifest.scenario_id,
        "channel": result.manifest.channel,
        "family": result.manifest.family,
        "version": result.manifest.version,
        "public_path": result.public_path,
        "result": _scenario_result(result),
        "drift_flags": list(result.drift_flags),
        "error_category": result.error_category,
        "started_at": result.started_at,
        "finished_at": result.finished_at,
        "telemetry_alignment": {
            "report_id": telemetry_views.snapshot.report_id,
            "entry_ref": telemetry_views.snapshot.entry_ref,
            "device_ref": trace.get("device_ref"),
            "mqtt_connected": telemetry_views.system_health.get("mqtt_connected"),
            "command_confirmation_avg_latency_seconds": telemetry_views.system_health.get(
                "command_confirmation_avg_latency_seconds"
            ),
            "refresh_avg_latency_seconds": telemetry_views.system_health.get(
                "refresh_avg_latency_seconds"
            ),
            "auth_refresh_success_count": telemetry_views.system_health.get(
                "auth_refresh_success_count"
            ),
        },
    }


def build_replay_run_summary(
    results: Sequence[ReplayExecutionResult],
    *,
    telemetry_views_by_scenario: Mapping[str, TelemetryViews],
) -> dict[str, Any]:
    """Build one stable replay run summary for downstream closeout/evidence use."""
    scenarios = [
        build_replay_scenario_summary(
            result,
            telemetry_views=telemetry_views_by_scenario[result.manifest.scenario_id],
        )
        for result in results
    ]
    passed_count = sum(1 for scenario in scenarios if scenario["result"] == "passed")
    return {
        "schema_version": _SCHEMA_VERSION,
        "scenario_count": len(scenarios),
        "passed_count": passed_count,
        "failed_count": len(scenarios) - passed_count,
        "scenarios": scenarios,
    }


__all__ = [
    "build_replay_run_summary",
    "build_replay_scenario_summary",
]
