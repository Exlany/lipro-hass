"""Meta guards for protocol replay manifests and deterministic controls."""

from __future__ import annotations

import json
from pathlib import Path

from tests.harness.protocol import iter_replay_manifests
from tests.harness.protocol.replay_report import EXPLICIT_REPLAY_ASSURANCE_FAMILIES
from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_REPLAY_ROOT = _ROOT / "tests" / "fixtures" / "protocol_replay"
_ALLOWED_AUTHORITY_PREFIXES = (
    "tests/fixtures/api_contracts/",
    "tests/fixtures/protocol_boundary/",
)


def test_replay_manifests_have_authority_pointer_version_and_deterministic_controls() -> None:
    manifests = iter_replay_manifests()

    assert manifests
    assert {manifest.channel for manifest in manifests} == {"rest", "mqtt"}
    for manifest in manifests:
        assert manifest.version == "v1"
        assert manifest.controls.seed > 0
        assert manifest.controls.clock_baseline.endswith("Z")
        assert manifest.authority_path.exists()
        assert manifest.assertion_families == ("canonical", "drift", "telemetry")
        assert any(
            f"tests/fixtures/{prefix}" in manifest.authority_path.as_posix()
            for prefix in ("api_contracts/", "protocol_boundary/")
        )


def test_replay_manifest_files_do_not_duplicate_authority_payload_truth() -> None:
    for manifest_path in sorted(_REPLAY_ROOT.rglob("*.json")):
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert "payload" not in payload
        assert "canonical" not in payload
        assert "fingerprint" not in payload
        authority_path = payload["authority_path"]
        assert isinstance(authority_path, str)
        assert authority_path.startswith(_ALLOWED_AUTHORITY_PREFIXES)


def test_phase_10_rest_replay_families_are_registered_with_expected_authority() -> None:
    manifests = {manifest.family: manifest for manifest in iter_replay_manifests(channel="rest")}

    expected = {
        "rest.list-envelope": (
            "tests/fixtures/api_contracts/get_device_list.compat.json",
            "protocol.contracts.normalize_list_envelope",
        ),
        "rest.device-list": (
            "tests/fixtures/api_contracts/get_device_list.compat.json",
            "protocol.contracts.normalize_device_list_page",
        ),
        "rest.device-status": (
            "tests/fixtures/api_contracts/query_device_status.mixed.json",
            "protocol.contracts.normalize_device_status_rows",
        ),
        "rest.mesh-group-status": (
            "tests/fixtures/api_contracts/query_mesh_group_status.topology.json",
            "protocol.contracts.normalize_mesh_group_status_rows",
        ),
        "rest.schedule-json": (
            "tests/fixtures/api_contracts/query_mesh_schedule_json.v1.json",
            "protocol.contracts.normalize_schedule_json",
        ),
    }

    assert expected.keys() <= manifests.keys()
    for family, (authority_path, operation) in expected.items():
        manifest = manifests[family]
        assert manifest.authority_path.as_posix().endswith(authority_path)
        assert manifest.operation == operation
        assert manifest.version == "v1"
        assert manifest.channel == "rest"


def test_phase_20_mqtt_replay_families_are_registered_with_expected_authority() -> None:
    manifests = {manifest.family: manifest for manifest in iter_replay_manifests(channel="mqtt")}

    expected = {
        "mqtt.topic": (
            "tests/fixtures/protocol_boundary/mqtt_topic.device_state.v1.json",
            "protocol.boundary.decode_mqtt_topic",
        ),
        "mqtt.message-envelope": (
            "tests/fixtures/protocol_boundary/mqtt_message_envelope.device_state.v1.json",
            "protocol.boundary.decode_mqtt_message_envelope",
        ),
        "mqtt.properties": (
            "tests/fixtures/protocol_boundary/mqtt_properties.device_state.v1.json",
            "protocol.boundary.decode_mqtt_properties",
        ),
    }

    assert expected.keys() <= manifests.keys()
    for family, (authority_path, operation) in expected.items():
        manifest = manifests[family]
        assert manifest.authority_path.as_posix().endswith(authority_path)
        assert manifest.operation == operation
        assert manifest.version == "v1"
        assert manifest.channel == "mqtt"


def test_phase_10_replay_readmes_document_boundary_first_rule() -> None:
    replay_readme = (_ROOT / "tests" / "fixtures" / "protocol_replay" / "README.md").read_text(encoding="utf-8")
    contract_readme = (_ROOT / "tests" / "fixtures" / "api_contracts" / "README.md").read_text(encoding="utf-8")
    boundary_readme = (_ROOT / "tests" / "fixtures" / "protocol_boundary" / "README.md").read_text(encoding="utf-8")

    for family in (
        "mqtt.topic",
        "mqtt.message-envelope",
        "rest.list-envelope",
        "rest.device-list",
        "rest.device-status",
        "rest.mesh-group-status",
        "rest.schedule-json",
    ):
        assert family in replay_readme

    for fixture_name in (
        "get_device_list.compat.json",
        "query_device_status.mixed.json",
        "query_mesh_group_status.topology.json",
        "query_mesh_schedule_json.v1.json",
    ):
        assert fixture_name in contract_readme

    for family in ("mqtt.topic", "mqtt.message-envelope", "mqtt.properties"):
        assert family in boundary_readme

    for fixture_name in (
        "mqtt_topic.device_state.v1.json",
        "mqtt_message_envelope.device_state.v1.json",
        "mqtt_properties.device_state.v1.json",
    ):
        assert fixture_name in boundary_readme

    assert "future-host rule" in contract_readme
    assert "CLI / other platforms may only reuse formal boundary contracts" in contract_readme
    assert "protocol contracts public path" in replay_readme


def test_phase_21_explicit_replay_assurance_families_stay_registered() -> None:
    manifests = {manifest.family for manifest in iter_replay_manifests()}

    assert EXPLICIT_REPLAY_ASSURANCE_FAMILIES == (
        "rest.list-envelope",
        "rest.schedule-json",
        "mqtt.topic",
        "mqtt.message-envelope",
    )
    assert set(EXPLICIT_REPLAY_ASSURANCE_FAMILIES).issubset(manifests)
