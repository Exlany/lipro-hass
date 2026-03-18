"""Integration-style tests for the protocol replay harness mainline."""

from __future__ import annotations

from dataclasses import replace

from custom_components.lipro.core.protocol.contracts import (
    CanonicalProtocolContracts,
    CanonicalScheduleJson,
)
from custom_components.lipro.core.protocol.facade import LiproProtocolFacade
from tests.core.api.test_protocol_contract_matrix import (
    EXPECTED_DEVICE_LIST_DEVICES,
    EXPECTED_DEVICE_STATUS_ROWS,
    EXPECTED_MESH_GROUP_STATUS_ROWS,
    EXPECTED_MQTT_CONFIG,
)
from tests.harness.headless_consumer import HEADLESS_PROOF_ASSERTION_FAMILIES
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
from tests.harness.protocol.replay_report import EXPLICIT_REPLAY_ASSURANCE_FAMILIES


class _FailingScheduleJsonContracts(CanonicalProtocolContracts):
    @staticmethod
    def normalize_schedule_json(_payload: object) -> CanonicalScheduleJson:
        raise ValueError("schedule-json representative failure")


class _FailingScheduleJsonProtocolFacade(LiproProtocolFacade):
    @property
    def contracts(self) -> CanonicalProtocolContracts:
        return _FailingScheduleJsonContracts()


def _expected_canonical_for_manifest(manifest) -> object:
    """Return the expected canonical contract for one replay manifest."""
    if manifest.channel == "mqtt":
        fixture = load_replay_fixture(manifest)
        return fixture.authority_metadata["canonical"]
    if manifest.family == "rest.mqtt-config":
        return EXPECTED_MQTT_CONFIG
    if manifest.family == "rest.list-envelope":
        fixture = load_replay_fixture(manifest)
        assert isinstance(fixture.authority_payload, dict)
        return {"rows": fixture.authority_payload["data"], "has_more": True}
    if manifest.family == "rest.device-list":
        return {
            "devices": EXPECTED_DEVICE_LIST_DEVICES,
            "has_more": True,
        }
    if manifest.family == "rest.device-status":
        return EXPECTED_DEVICE_STATUS_ROWS
    if manifest.family == "rest.mesh-group-status":
        return EXPECTED_MESH_GROUP_STATUS_ROWS
    if manifest.family == "rest.schedule-json":
        return {"days": [1, 3], "time": [3600, 7200], "evt": [0, 1]}
    msg = f"Unhandled replay manifest family: {manifest.family}"
    raise AssertionError(msg)


def test_protocol_replay_harness_runs_all_registered_manifests_in_order() -> None:
    manifests = iter_replay_manifests()
    driver = ProtocolReplayDriver()

    manifest_paths = [manifest.manifest_path.as_posix() for manifest in manifests]
    results = [driver.run_manifest(manifest) for manifest in manifests]

    assert manifest_paths == sorted(manifest_paths)
    assert {manifest.family for manifest in manifests} >= {
        "mqtt.topic",
        "mqtt.message-envelope",
        "mqtt.properties",
        "rest.mqtt-config",
        "rest.list-envelope",
        "rest.device-list",
        "rest.device-status",
        "rest.mesh-group-status",
        "rest.schedule-json",
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
    manifests = {
        manifest.family: manifest
        for manifest in iter_replay_manifests()
        if manifest.family in EXPLICIT_REPLAY_ASSURANCE_FAMILIES
    }
    driver = ProtocolReplayDriver()
    list_envelope_result = driver.run_manifest(manifests["rest.list-envelope"])
    error_result = ProtocolReplayDriver(
        protocol_factory=_FailingScheduleJsonProtocolFacade
    ).run_manifest(manifests["rest.schedule-json"])
    topic_result = driver.run_manifest(manifests["mqtt.topic"])
    drift_result = replace(
        driver.run_manifest(manifests["mqtt.message-envelope"]),
        drift_flags=("fingerprint_mismatch",),
    )

    telemetry_views = {
        list_envelope_result.manifest.scenario_id: assert_exporter_backed_replay_telemetry(
            list_envelope_result.manifest,
            list_envelope_result,
        ),
        error_result.manifest.scenario_id: assert_exporter_backed_replay_telemetry(
            error_result.manifest,
            error_result,
        ),
        topic_result.manifest.scenario_id: assert_exporter_backed_replay_telemetry(
            topic_result.manifest,
            topic_result,
        ),
        drift_result.manifest.scenario_id: assert_exporter_backed_replay_telemetry(
            drift_result.manifest,
            drift_result,
        ),
    }

    summary = build_replay_run_summary(
        [list_envelope_result, error_result, topic_result, drift_result],
        telemetry_views_by_scenario=telemetry_views,
    )
    coverage_by_family = {
        entry["family"]: entry for entry in summary["explicit_family_coverage"]
    }
    representative_story = summary["representative_failure_drift"]

    assert summary["schema_version"] == "replay.report.v1"
    assert summary["scenario_count"] == 4
    assert summary["passed_count"] == 2
    assert summary["failed_count"] == 2
    assert summary["scenarios"][0]["result"] == "passed"
    assert summary["scenarios"][1]["error_category"] == "protocol"
    assert summary["scenarios"][1]["error_type"] == "ValueError"
    assert summary["scenarios"][1]["failure_summary"] == {
        "failure_category": "protocol",
        "failure_origin": "protocol.replay",
        "handling_policy": "inspect",
        "error_type": "ValueError",
    }
    assert summary["scenarios"][3]["drift_flags"] == ["fingerprint_mismatch"]
    assert summary["scenarios"][3]["failure_summary"] == {
        "failure_category": None,
        "failure_origin": None,
        "handling_policy": None,
        "error_type": None,
    }
    assert summary["scenarios"][0]["telemetry_alignment"]["device_ref"].startswith("device_")
    assert [entry["family"] for entry in summary["explicit_family_coverage"]] == list(
        EXPLICIT_REPLAY_ASSURANCE_FAMILIES
    )
    assert coverage_by_family["rest.list-envelope"]["public_paths"] == [
        "LiproProtocolFacade.contracts.normalize_list_envelope"
    ]
    assert coverage_by_family["rest.schedule-json"]["results"] == ["failed"]
    assert coverage_by_family["mqtt.topic"]["results"] == ["passed"]
    assert coverage_by_family["mqtt.message-envelope"]["results"] == ["failed"]
    assert representative_story["remaining_family_channels"] == ["rest", "mqtt"]
    assert [
        scenario["family"]
        for scenario in representative_story["remaining_family_representatives"]
    ] == ["rest.schedule-json", "mqtt.message-envelope"]
    assert representative_story["error_scenarios"][0]["public_path"] == (
        "LiproProtocolFacade.contracts.normalize_schedule_json"
    )
    assert representative_story["error_scenarios"][0]["error_category"] == "protocol"
    assert representative_story["error_scenarios"][0]["error_type"] == "ValueError"
    assert representative_story["drift_scenarios"][0]["public_path"] == (
        "core.protocol.boundary.decode_mqtt_message_envelope_payload"
    )
