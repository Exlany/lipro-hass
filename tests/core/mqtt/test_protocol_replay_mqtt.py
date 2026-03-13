"""Replay assertions for representative MQTT protocol scenarios."""

from __future__ import annotations

import pytest

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

_MQTT_MANIFESTS = iter_replay_manifests(channel="mqtt")


@pytest.mark.parametrize(
    "manifest",
    _MQTT_MANIFESTS,
    ids=lambda manifest: manifest.scenario_id,
)
def test_mqtt_replay_scenarios_use_boundary_decoder_public_path(
    manifest: ReplayManifest,
) -> None:
    driver = ProtocolReplayDriver()
    fixture = load_replay_fixture(manifest)

    result = driver.run_fixture(fixture)

    assert result.public_path == "core.protocol.boundary.decode_mqtt_properties_payload"
    assert_replay_has_no_drift(
        result,
        expected_family="mqtt.properties",
        expected_version="v1",
    )
    assert_replay_canonical_contract(
        result,
        expected_canonical=fixture.authority_metadata["canonical"],
        expected_fingerprint=fixture.authority_metadata["fingerprint"],
    )
    views = assert_exporter_backed_replay_telemetry(manifest, result)
    assert views.system_health["mqtt_connected"] is True
