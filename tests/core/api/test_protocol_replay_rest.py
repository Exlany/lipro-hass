"""Replay assertions for representative REST protocol scenarios."""

from __future__ import annotations

import pytest

from tests.core.api.test_protocol_contract_matrix import EXPECTED_MQTT_CONFIG
from tests.harness.protocol import ProtocolReplayDriver, iter_replay_manifests
from tests.harness.protocol.replay_assertions import (
    assert_exporter_backed_replay_telemetry,
    assert_replay_canonical_contract,
    assert_replay_has_no_drift,
)
from tests.harness.protocol.replay_models import ReplayManifest

_REST_MANIFESTS = iter_replay_manifests(channel="rest")


@pytest.mark.parametrize(
    "manifest",
    _REST_MANIFESTS,
    ids=lambda manifest: manifest.scenario_id,
)
def test_rest_replay_scenarios_use_unified_protocol_root(manifest: ReplayManifest) -> None:
    driver = ProtocolReplayDriver()

    result = driver.run_manifest(manifest)

    assert result.public_path == "LiproProtocolFacade.contracts.normalize_mqtt_config"
    assert_replay_has_no_drift(
        result,
        expected_family="rest.mqtt-config",
        expected_version="v1",
    )
    assert_replay_canonical_contract(
        result,
        expected_canonical=EXPECTED_MQTT_CONFIG,
    )
    views = assert_exporter_backed_replay_telemetry(manifest, result)
    assert views.system_health["auth_refresh_success_count"] == 1
