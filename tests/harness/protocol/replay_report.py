"""Structured replay-run summary builders for assurance evidence."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from custom_components.lipro.core.telemetry.models import (
    TelemetryViews,
    extract_failure_summary,
)
from tests.harness.protocol.replay_models import ReplayExecutionResult

_SCHEMA_VERSION = "replay.report.v1"
EXPLICIT_REPLAY_ASSURANCE_FAMILIES = (
    "rest.list-envelope",
    "rest.schedule-json",
    "mqtt.topic",
    "mqtt.message-envelope",
)


def _scenario_result(result: ReplayExecutionResult) -> str:
    if result.error_type is not None or result.drift_flags:
        return "failed"
    return "passed"


def _dedupe_strings(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _scenario_projection(scenario: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "scenario_id": scenario["scenario_id"],
        "channel": scenario["channel"],
        "family": scenario["family"],
        "version": scenario["version"],
        "public_path": scenario["public_path"],
        "result": scenario["result"],
        "drift_flags": list(scenario["drift_flags"]),
        "error_category": scenario["error_category"],
        "error_type": scenario["error_type"],
        "failure_summary": dict(scenario["failure_summary"]),
    }


def _build_explicit_family_coverage(
    scenarios: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    coverage: list[dict[str, Any]] = []
    for family in EXPLICIT_REPLAY_ASSURANCE_FAMILIES:
        family_scenarios = [scenario for scenario in scenarios if scenario["family"] == family]
        coverage.append(
            {
                "family": family,
                "scenario_count": len(family_scenarios),
                "scenario_ids": [scenario["scenario_id"] for scenario in family_scenarios],
                "channels": _dedupe_strings(
                    [str(scenario["channel"]) for scenario in family_scenarios]
                ),
                "public_paths": _dedupe_strings(
                    [str(scenario["public_path"]) for scenario in family_scenarios]
                ),
                "assertion_families": _dedupe_strings(
                    [
                        assertion_family
                        for scenario in family_scenarios
                        for assertion_family in scenario["assertion_families"]
                    ]
                ),
                "results": [scenario["result"] for scenario in family_scenarios],
            }
        )
    return coverage


def _build_representative_failure_drift(
    scenarios: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    failure_candidates = [
        scenario
        for scenario in scenarios
        if scenario["error_category"] is not None or scenario["drift_flags"]
    ]
    error_scenarios = [
        _scenario_projection(scenario)
        for scenario in failure_candidates
        if scenario["error_category"] is not None
    ]
    drift_scenarios = [
        _scenario_projection(scenario)
        for scenario in failure_candidates
        if scenario["drift_flags"] and scenario["error_category"] is None
    ]
    remaining_family_representatives = [
        _scenario_projection(scenario)
        for family in EXPLICIT_REPLAY_ASSURANCE_FAMILIES
        for scenario in failure_candidates
        if scenario["family"] == family
    ]
    return {
        "error_scenarios": error_scenarios,
        "drift_scenarios": drift_scenarios,
        "remaining_family_channels": _dedupe_strings(
            [str(scenario["channel"]) for scenario in remaining_family_representatives]
        ),
        "remaining_family_representatives": remaining_family_representatives,
    }


def _scenario_failure_summary(
    result: ReplayExecutionResult,
    *,
    telemetry_views: TelemetryViews,
) -> dict[str, str | None]:
    failure_summary = extract_failure_summary(
        telemetry_views.system_health,
        default_origin="protocol.replay",
        raw_error_keys=(),
    )
    if (
        failure_summary["failure_category"] is None
        and failure_summary["error_type"] is None
    ):
        return dict(result.failure_summary)
    return dict(failure_summary)


def build_replay_scenario_summary(
    result: ReplayExecutionResult,
    *,
    telemetry_views: TelemetryViews,
) -> dict[str, Any]:
    """Build one replay scenario summary row."""
    trace = telemetry_views.diagnostics["runtime"]["recent_command_traces"][0]
    failure_summary = _scenario_failure_summary(result, telemetry_views=telemetry_views)
    return {
        "scenario_id": result.manifest.scenario_id,
        "channel": result.manifest.channel,
        "family": result.manifest.family,
        "version": result.manifest.version,
        "assertion_families": list(result.manifest.assertion_families),
        "public_path": result.public_path,
        "result": _scenario_result(result),
        "drift_flags": list(result.drift_flags),
        "error_category": failure_summary["failure_category"],
        "error_type": failure_summary["error_type"],
        "failure_summary": failure_summary,
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
        "explicit_family_coverage": _build_explicit_family_coverage(scenarios),
        "representative_failure_drift": _build_representative_failure_drift(scenarios),
        "scenarios": scenarios,
    }


__all__ = [
    "EXPLICIT_REPLAY_ASSURANCE_FAMILIES",
    "build_replay_run_summary",
    "build_replay_scenario_summary",
]
