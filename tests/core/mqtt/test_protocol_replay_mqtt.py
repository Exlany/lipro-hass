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
_EXPLICIT_MQTT_ASSURANCE_FAMILIES = (
    "mqtt.topic",
    "mqtt.message-envelope",
)
_EXPECTED_PUBLIC_PATHS = {
    "mqtt.topic": "core.protocol.boundary.decode_mqtt_topic_payload",
    "mqtt.message-envelope": "core.protocol.boundary.decode_mqtt_message_envelope_payload",
    "mqtt.properties": "core.protocol.boundary.decode_mqtt_properties_payload",
}


def _assert_mqtt_contract_shape(manifest: ReplayManifest, canonical: object) -> None:
    assert isinstance(canonical, dict)
    if manifest.family == "mqtt.topic":
        assert canonical.keys() == {"bizId", "deviceId", "topicFamily"}
        return
    if manifest.family == "mqtt.message-envelope":
        assert canonical
        assert all(isinstance(key, str) for key in canonical)
        return
    if manifest.family == "mqtt.properties":
        assert all(isinstance(key, str) for key in canonical)


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

    assert result.public_path == _EXPECTED_PUBLIC_PATHS[manifest.family]
    assert_replay_has_no_drift(
        result,
        expected_family=manifest.family,
        expected_version="v1",
    )
    assert_replay_canonical_contract(
        result,
        expected_canonical=fixture.authority_metadata["canonical"],
        expected_fingerprint=fixture.authority_metadata["fingerprint"],
    )
    _assert_mqtt_contract_shape(manifest, result.canonical)
    views = assert_exporter_backed_replay_telemetry(manifest, result)
    assert views.system_health["mqtt_connected"] is True


def test_mqtt_remaining_families_have_explicit_replay_coverage_contract() -> None:
    manifests = {manifest.family: manifest for manifest in _MQTT_MANIFESTS}
    driver = ProtocolReplayDriver()

    assert set(_EXPLICIT_MQTT_ASSURANCE_FAMILIES) <= manifests.keys()
    for family in _EXPLICIT_MQTT_ASSURANCE_FAMILIES:
        manifest = manifests[family]
        fixture = load_replay_fixture(manifest)
        result = driver.run_fixture(fixture)

        assert result.public_path == _EXPECTED_PUBLIC_PATHS[family]
        assert_replay_has_no_drift(
            result,
            expected_family=family,
            expected_version="v1",
        )
        assert_replay_canonical_contract(
            result,
            expected_canonical=fixture.authority_metadata["canonical"],
            expected_fingerprint=fixture.authority_metadata["fingerprint"],
        )
        _assert_mqtt_contract_shape(manifest, result.canonical)
