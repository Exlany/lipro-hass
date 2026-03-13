"""Integration-style tests for the protocol replay harness mainline."""

from __future__ import annotations

from dataclasses import replace

from tests.core.api.test_protocol_contract_matrix import EXPECTED_MQTT_CONFIG
from tests.harness.protocol import (
    ProtocolReplayDriver,
    build_replay_run_summary,
    iter_replay_manifests,
    load_replay_fixture,
)
from tests.harness.protocol.replay_assertions import (
    assert_exporter_backed_replay_telemetry,
    assert_replay_canonical_contract,
)


def test_protocol_replay_harness_runs_all_registered_manifests_in_order() -> None:
    manifests = iter_replay_manifests()
    driver = ProtocolReplayDriver()

    scenario_ids = [manifest.scenario_id for manifest in manifests]
    results = [driver.run_manifest(manifest) for manifest in manifests]

    assert scenario_ids == [
        "mqtt.device_state.v1",
        "rest.get_mqtt_config.direct.v1",
        "rest.get_mqtt_config.wrapped.v1",
    ]
    assert all(result.error_category is None for result in results)
    assert results[1].canonical == EXPECTED_MQTT_CONFIG
    assert results[1].canonical == results[2].canonical


def test_protocol_replay_harness_pulls_telemetry_assertions_from_exporter_truth() -> None:
    driver = ProtocolReplayDriver()

    for manifest in iter_replay_manifests():
        fixture = load_replay_fixture(manifest)
        result = driver.run_fixture(fixture)
        views = assert_exporter_backed_replay_telemetry(manifest, result)
        assert views.ci["summary"]["command_confirmation_timeout_total"] == 0
        if manifest.channel == "mqtt":
            assert_replay_canonical_contract(
                result,
                expected_canonical=fixture.authority_metadata["canonical"],
                expected_fingerprint=fixture.authority_metadata["fingerprint"],
            )
        else:
            assert_replay_canonical_contract(
                result,
                expected_canonical=EXPECTED_MQTT_CONFIG,
            )


def test_protocol_replay_harness_builds_structured_run_summary() -> None:
    manifests = iter_replay_manifests()
    driver = ProtocolReplayDriver()
    good_result = driver.run_manifest(manifests[0])
    drift_result = replace(good_result, drift_flags=("fingerprint_mismatch",))
    error_manifest = replace(manifests[1], operation="protocol.unsupported")
    error_result = driver.run_manifest(error_manifest)

    telemetry_views = {
        good_result.manifest.scenario_id: assert_exporter_backed_replay_telemetry(
            good_result.manifest,
            good_result,
        ),
        drift_result.manifest.scenario_id: assert_exporter_backed_replay_telemetry(
            drift_result.manifest,
            drift_result,
        ),
        error_result.manifest.scenario_id: assert_exporter_backed_replay_telemetry(
            error_result.manifest,
            error_result,
        ),
    }

    summary = build_replay_run_summary(
        [good_result, drift_result, error_result],
        telemetry_views_by_scenario=telemetry_views,
    )

    assert summary["schema_version"] == "replay.report.v1"
    assert summary["scenario_count"] == 3
    assert summary["passed_count"] == 1
    assert summary["failed_count"] == 2
    assert summary["scenarios"][0]["result"] == "passed"
    assert summary["scenarios"][1]["drift_flags"] == ["fingerprint_mismatch"]
    assert summary["scenarios"][2]["error_category"] == "ValueError"
    assert summary["scenarios"][0]["telemetry_alignment"]["device_ref"].startswith("device_")
