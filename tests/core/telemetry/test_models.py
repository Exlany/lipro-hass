"""Tests for telemetry contracts."""

from __future__ import annotations

from custom_components.lipro.core.telemetry import (
    CardinalityBudget,
    TelemetrySensitivity,
    TelemetrySnapshot,
    TelemetryViews,
)
from custom_components.lipro.core.telemetry.models import (
    build_failure_summary,
    extract_failure_summary,
)


def test_telemetry_sensitivity_blocks_credential_equivalent_fields() -> None:
    sensitivity = TelemetrySensitivity()

    assert sensitivity.is_blocked("password_hash") is True
    assert sensitivity.is_blocked("access_token") is True
    assert sensitivity.is_blocked("secret_key") is True
    assert sensitivity.is_blocked("safe_key") is False


def test_telemetry_sensitivity_maps_pseudonymous_reference_aliases() -> None:
    sensitivity = TelemetrySensitivity()

    assert sensitivity.reference_alias_for("entry_id") == "entry_ref"
    assert sensitivity.reference_alias_for("device_serial") == "device_ref"
    assert sensitivity.reference_alias_for("gateway_device_id") == "device_ref"
    assert sensitivity.reference_alias_for("trace_count") is None


def test_snapshot_and_views_are_json_friendly() -> None:
    snapshot = TelemetrySnapshot(
        schema_version="telemetry.v1",
        report_id="report_1",
        generated_at=123.0,
        entry_ref="entry_deadbeef",
        protocol={"telemetry": {"mqtt_connected": True}},
        runtime={"device_count": 2},
    )
    views = TelemetryViews(
        snapshot=snapshot,
        diagnostics={"schema_version": "telemetry.v1"},
        system_health={"device_count": 2},
        developer={"debug": True},
        ci={"summary": {"device_count": 2}},
    )

    assert snapshot.to_dict()["entry_ref"] == "entry_deadbeef"
    assert views.to_dict()["snapshot"]["report_id"] == "report_1"
    assert views.to_dict()["ci"]["summary"]["device_count"] == 2


def test_cardinality_budget_defaults_stay_bounded() -> None:
    budget = CardinalityBudget()

    assert budget.max_mapping_items == 32
    assert budget.max_sequence_items == 20
    assert budget.max_string_length == 256


def test_build_failure_summary_normalizes_category_and_policy() -> None:
    assert build_failure_summary(
        error_type="ValueError",
        failure_origin="protocol.replay",
    ) == {
        "failure_category": "protocol",
        "failure_origin": "protocol.replay",
        "handling_policy": "inspect",
        "error_type": "ValueError",
    }


def test_extract_failure_summary_prefers_explicit_payload_and_raw_fallback() -> None:
    explicit = extract_failure_summary(
        {
            "failure_summary": {
                "failure_category": "runtime",
                "failure_origin": "runtime.update",
                "handling_policy": "inspect",
                "error_type": "RuntimeError",
            }
        },
        default_origin="protocol.mqtt",
        raw_error_keys=("mqtt_last_error_type",),
    )
    fallback = extract_failure_summary(
        {"mqtt_last_error_type": "TimeoutError"},
        default_origin="protocol.mqtt",
        raw_error_keys=("mqtt_last_error_type",),
    )

    assert explicit == {
        "failure_category": "runtime",
        "failure_origin": "runtime.update",
        "handling_policy": "inspect",
        "error_type": "RuntimeError",
    }
    assert fallback == {
        "failure_category": "network",
        "failure_origin": "protocol.mqtt",
        "handling_policy": "retry",
        "error_type": "TimeoutError",
    }
