"""Meta guards for protocol replay manifests and deterministic controls."""

from __future__ import annotations

import json
from pathlib import Path

from tests.harness.protocol import iter_replay_manifests
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
