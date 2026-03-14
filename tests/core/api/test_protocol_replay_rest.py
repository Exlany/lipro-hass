"""Replay assertions for representative REST protocol scenarios."""

from __future__ import annotations

import pytest

from tests.core.api.test_protocol_contract_matrix import (
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
_EXPECTED_PUBLIC_PATHS = {
    "rest.mqtt-config": "LiproProtocolFacade.contracts.normalize_mqtt_config",
    "rest.device-list": "LiproProtocolFacade.contracts.normalize_device_list_page",
    "rest.device-status": "LiproProtocolFacade.contracts.normalize_device_status_rows",
    "rest.mesh-group-status": "LiproProtocolFacade.contracts.normalize_mesh_group_status_rows",
}
_EXPECTED_CANONICAL = {
    "rest.mqtt-config": EXPECTED_MQTT_CONFIG,
    "rest.device-list": {
        "devices": EXPECTED_DEVICE_LIST_DEVICES,
        "has_more": True,
    },
    "rest.device-status": EXPECTED_DEVICE_STATUS_ROWS,
    "rest.mesh-group-status": EXPECTED_MESH_GROUP_STATUS_ROWS,
}


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
        expected_canonical=_EXPECTED_CANONICAL[manifest.family],
    )
    views = assert_exporter_backed_replay_telemetry(manifest, result)
    assert views.system_health["auth_refresh_success_count"] == 1
    assert fixture.authority_payload is not None
