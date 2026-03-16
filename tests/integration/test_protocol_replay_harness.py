"""Integration-style tests for the protocol replay harness mainline."""

from __future__ import annotations

from dataclasses import replace

from tests.core.api.test_protocol_contract_matrix import (
    EXPECTED_DEVICE_LIST_DEVICES,
    EXPECTED_DEVICE_STATUS_ROWS,
    EXPECTED_MESH_GROUP_STATUS_ROWS,
    EXPECTED_MQTT_CONFIG,
)
from tests.harness.headless_consumer import HEADLESS_PROOF_ASSERTION_FAMILIES
from tests.harness.protocol import (
    LoadedReplayFixture,
    ProtocolReplayDriver,
    build_replay_run_summary,
    iter_replay_manifests,
    load_replay_fixture,
)
from tests.harness.protocol.replay_assertions import (
    assert_exporter_backed_replay_telemetry,
    assert_replay_canonical_contract,
)


def _expected_canonical_for_manifest(manifest) -> object:
    """Return the expected canonical contract for one replay manifest."""
    if manifest.channel == "mqtt":
        fixture = load_replay_fixture(manifest)
        return fixture.authority_metadata["canonical"]
    if manifest.family == "rest.mqtt-config":
        return EXPECTED_MQTT_CONFIG
    if manifest.family == "rest.device-list":
        return {
            "devices": EXPECTED_DEVICE_LIST_DEVICES,
            "has_more": True,
        }
    if manifest.family == "rest.device-status":
        return EXPECTED_DEVICE_STATUS_ROWS
    if manifest.family == "rest.mesh-group-status":
        return EXPECTED_MESH_GROUP_STATUS_ROWS
    msg = f"Unhandled replay manifest family: {manifest.family}"
    raise AssertionError(msg)


def test_protocol_replay_harness_runs_all_registered_manifests_in_order() -> None:
    manifests = iter_replay_manifests()
    driver = ProtocolReplayDriver()

    manifest_paths = [manifest.manifest_path.as_posix() for manifest in manifests]
    results = [driver.run_manifest(manifest) for manifest in manifests]

    assert manifest_paths == sorted(manifest_paths)
    assert {manifest.family for manifest in manifests} >= {
        "mqtt.properties",
        "rest.mqtt-config",
        "rest.device-list",
        "rest.device-status",
        "rest.mesh-group-status",
    }
    assert all(result.error_category is None for result in results)
    for manifest, result in zip(manifests, results, strict=True):
        assert result.canonical == _expected_canonical_for_manifest(manifest)

    mqtt_config_results = [
        result
        for manifest, result in zip(manifests, results, strict=True)
        if manifest.family == "rest.mqtt-config"
    ]
    assert len(mqtt_config_results) >= 2
    assert all(result.canonical == EXPECTED_MQTT_CONFIG for result in mqtt_config_results)


def test_protocol_replay_harness_pulls_telemetry_assertions_from_exporter_truth() -> None:
    driver = ProtocolReplayDriver()

    for manifest in iter_replay_manifests():
        fixture = load_replay_fixture(manifest)
        result = driver.run_fixture(fixture)
        views = assert_exporter_backed_replay_telemetry(manifest, result)
        assert views.ci["summary"]["command_confirmation_timeout_total"] == 0
        expected_fingerprint = (
            fixture.authority_metadata["fingerprint"]
            if manifest.channel == "mqtt"
            else None
        )
        assert_replay_canonical_contract(
            result,
            expected_canonical=_expected_canonical_for_manifest(manifest),
            expected_fingerprint=expected_fingerprint,
        )


def test_protocol_replay_harness_covers_headless_proof_families() -> None:
    assert set(HEADLESS_PROOF_ASSERTION_FAMILIES).issubset(
        {manifest.family for manifest in iter_replay_manifests()}
    )


def test_protocol_replay_harness_builds_structured_run_summary() -> None:
    manifests = iter_replay_manifests()
    driver = ProtocolReplayDriver()
    good_result = driver.run_manifest(manifests[0])
    drift_result = replace(good_result, drift_flags=("fingerprint_mismatch",))
    error_manifest = next(
        manifest for manifest in manifests if manifest.family == "rest.mqtt-config"
    )
    error_result = driver.run_fixture(
        LoadedReplayFixture(
            manifest=error_manifest,
            authority_payload="bad",
            authority_metadata={},
        )
    )

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
