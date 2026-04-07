"""Replay assertions for representative REST protocol scenarios."""

from __future__ import annotations

import pytest

from tests.core.api.test_protocol_contract_boundary_decoders import (
    EXPECTED_DEVICE_LIST_DEVICES,
    EXPECTED_DEVICE_STATUS_ROWS,
    EXPECTED_MESH_GROUP_STATUS_ROWS,
    EXPECTED_MQTT_CONFIG,
)
from tests.harness.protocol import (
    ProtocolReplayDriver,
    iter_replay_manifests,
    load_replay_fixture,
)
from tests.harness.protocol.replay_assertions import (
    assert_exporter_backed_replay_telemetry,
    assert_replay_canonical_contract,
    assert_replay_has_no_drift,
)
from tests.harness.protocol.replay_models import ReplayManifest

_REST_MANIFESTS = iter_replay_manifests(channel="rest")
_EXPLICIT_REST_ASSURANCE_FAMILIES = (
    "rest.list-envelope",
    "rest.schedule-json",
)
_EXPECTED_PUBLIC_PATHS = {
    "rest.mqtt-config": "LiproProtocolFacade.contracts.normalize_mqtt_config",
    "rest.list-envelope": "LiproProtocolFacade.contracts.normalize_list_envelope",
    "rest.device-list": "LiproProtocolFacade.contracts.normalize_device_list_page",
    "rest.device-status": "LiproProtocolFacade.contracts.normalize_device_status_rows",
    "rest.mesh-group-status": "LiproProtocolFacade.contracts.normalize_mesh_group_status_rows",
    "rest.schedule-json": "LiproProtocolFacade.contracts.normalize_schedule_json",
}


def _assert_rest_contract_shape(manifest: ReplayManifest, canonical: object) -> None:
    if manifest.family == "rest.mqtt-config":
        assert isinstance(canonical, dict)
        assert canonical.keys() == {"accessKey", "secretKey", "endpoint", "clientId"}
        return
    if manifest.family == "rest.list-envelope":
        assert isinstance(canonical, dict)
        assert canonical.keys() >= {"rows", "has_more"}
        assert isinstance(canonical["rows"], list)
        assert all(isinstance(row, dict) for row in canonical["rows"])
        return
    if manifest.family == "rest.device-list":
        assert isinstance(canonical, dict)
        assert canonical.keys() >= {"devices", "has_more"}
        assert isinstance(canonical["devices"], list)
        assert all(
            row.keys() >= {
                "deviceId",
                "serial",
                "deviceName",
                "type",
                "iotName",
                "isGroup",
                "properties",
                "identityAliases",
            }
            for row in canonical["devices"]
        )
        return
    if manifest.family == "rest.device-status":
        assert isinstance(canonical, list)
        assert all(row.keys() == {"deviceId", "properties"} for row in canonical)
        return
    if manifest.family == "rest.mesh-group-status":
        assert isinstance(canonical, list)
        assert all(
            row.keys() >= {"groupId", "gatewayDeviceId", "devices", "properties"}
            for row in canonical
        )
        return
    if manifest.family == "rest.schedule-json":
        assert isinstance(canonical, dict)
        assert canonical.keys() == {"days", "time", "evt"}


def _expected_canonical(manifest: ReplayManifest) -> object:
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
    msg = f"Unhandled REST replay family: {manifest.family}"
    raise AssertionError(msg)


@pytest.mark.parametrize(
    "manifest",
    _REST_MANIFESTS,
    ids=lambda manifest: manifest.scenario_id,
)
def test_rest_replay_scenarios_use_unified_protocol_root(manifest: ReplayManifest) -> None:
    driver = ProtocolReplayDriver()
    fixture = load_replay_fixture(manifest)

    result = driver.run_manifest(manifest)

    assert result.public_path == _EXPECTED_PUBLIC_PATHS[manifest.family]
    assert_replay_has_no_drift(
        result,
        expected_family=manifest.family,
        expected_version="v1",
    )
    assert_replay_canonical_contract(
        result,
        expected_canonical=_expected_canonical(manifest),
    )
    _assert_rest_contract_shape(manifest, result.canonical)
    views = assert_exporter_backed_replay_telemetry(manifest, result)
    assert views.system_health["auth_refresh_success_count"] == 1
    assert fixture.authority_payload is not None


def test_rest_remaining_families_have_explicit_replay_coverage_contract() -> None:
    manifests = {manifest.family: manifest for manifest in _REST_MANIFESTS}
    driver = ProtocolReplayDriver()

    assert set(_EXPLICIT_REST_ASSURANCE_FAMILIES) <= manifests.keys()
    for family in _EXPLICIT_REST_ASSURANCE_FAMILIES:
        manifest = manifests[family]
        result = driver.run_manifest(manifest)

        assert result.public_path == _EXPECTED_PUBLIC_PATHS[family]
        assert_replay_has_no_drift(
            result,
            expected_family=family,
            expected_version="v1",
        )
        assert_replay_canonical_contract(
            result,
            expected_canonical=_expected_canonical(manifest),
        )
        _assert_rest_contract_shape(manifest, result.canonical)
