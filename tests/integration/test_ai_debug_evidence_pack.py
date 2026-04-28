"""Integration-style tests for the AI debug evidence-pack exporter."""

from __future__ import annotations

from dataclasses import replace
import json

from custom_components.lipro.core.telemetry.models import build_failure_summary
from scripts.export_ai_debug_evidence_pack import export_ai_debug_evidence_pack
from tests.harness.evidence_pack.collector import AiDebugEvidenceCollector
from tests.harness.evidence_pack.schema import (
    EVIDENCE_PACK_SCHEMA_VERSION,
    PACK_SECTIONS,
)
from tests.harness.evidence_pack.sources import (
    API_CONTRACT_ROOT,
    NON_AUTHORITY_PROOF_PATHS,
)
from tests.harness.protocol import ProtocolReplayDriver
from tests.harness.protocol.replay_report import EXPLICIT_REPLAY_ASSURANCE_FAMILIES

_FIXED_GENERATED_AT = "2026-03-13T00:00:00Z"


class _RepresentativeFailureDriftDriver:
    def __init__(self) -> None:
        self._driver = ProtocolReplayDriver()

    def run_manifest(self, manifest):
        result = self._driver.run_manifest(manifest)
        if manifest.family == "rest.schedule-json":
            return replace(
                result,
                canonical=None,
                drift_flags=("driver_error",),
                error_category="protocol",
                error_type="ValueError",
                failure_summary=build_failure_summary(
                    error_type="ValueError",
                    failure_origin="protocol.replay",
                ),
            )
        if manifest.family == "mqtt.message-envelope":
            return replace(result, drift_flags=("fingerprint_mismatch",))
        return result


def _load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_pack_exporter_writes_json_and_markdown_index(tmp_path) -> None:
    json_path, index_path = export_ai_debug_evidence_pack(
        tmp_path,
        report_id="phase8-report",
        generated_at=_FIXED_GENERATED_AT,
    )

    payload = _load_json(json_path)
    index_text = index_path.read_text(encoding="utf-8")

    assert json_path.name == "ai_debug_evidence_pack.json"
    assert index_path.name == "ai_debug_evidence_pack.index.md"
    assert set(payload) == set(PACK_SECTIONS)
    assert payload["metadata"]["schema_version"] == EVIDENCE_PACK_SCHEMA_VERSION
    assert payload["metadata"]["generated_at"] == _FIXED_GENERATED_AT
    assert payload["telemetry"]["view_count"] == len(payload["telemetry"]["views"])
    assert payload["replay"]["summary"]["scenario_count"] == len(
        payload["replay"]["summary"]["scenarios"]
    )
    assert payload["boundary"]["representative_families"]
    assert [
        family["family"]
        for family in payload["replay"]["summary"]["explicit_family_coverage"]
    ] == list(EXPLICIT_REPLAY_ASSURANCE_FAMILIES)
    assert [
        family["family"]
        for family in payload["boundary"]["remaining_family_projections"]
    ] == list(EXPLICIT_REPLAY_ASSURANCE_FAMILIES)
    assert payload["governance"]["verify_commands"]
    first_view = payload["telemetry"]["views"][0]
    assert "failure_summary" in first_view["diagnostics"]
    assert "failure_summary" in first_view["system_health"]
    assert "failure_summary" in first_view["developer"]
    assert "# AI Debug Evidence Pack Index" in index_text
    assert "`report_id`: `phase8-report`" in index_text
    assert "### telemetry" in index_text


def test_evidence_pack_preserves_real_timestamps_and_report_local_refs() -> None:
    collector = AiDebugEvidenceCollector()
    first = collector.collect(
        report_id="report-one", generated_at=_FIXED_GENERATED_AT
    ).to_dict()
    second = collector.collect(
        report_id="report-two", generated_at=_FIXED_GENERATED_AT
    ).to_dict()

    first_view = first["telemetry"]["views"][0]
    first_scenario = first["replay"]["summary"]["scenarios"][0]
    second_view = second["telemetry"]["views"][0]

    assert isinstance(first_view["snapshot"]["generated_at"], float)
    assert first_scenario["started_at"].endswith("Z")
    assert first_scenario["finished_at"].endswith("Z")
    assert (
        first_view["snapshot"]["entry_ref"]
        == first_scenario["telemetry_alignment"]["entry_ref"]
    )
    assert (
        first_view["snapshot"]["runtime"]["recent_command_traces"][0]["device_ref"]
        == first_scenario["telemetry_alignment"]["device_ref"]
    )
    assert first_view["snapshot"]["entry_ref"] != second_view["snapshot"]["entry_ref"]
    assert (
        first_view["snapshot"]["runtime"]["recent_command_traces"][0]["device_ref"]
        != second_view["snapshot"]["runtime"]["recent_command_traces"][0]["device_ref"]
    )


def test_evidence_pack_authority_trace_stays_on_formal_truth_for_headless_proof() -> (
    None
):
    payload = (
        AiDebugEvidenceCollector()
        .collect(
            report_id="headless-proof-authority",
            generated_at=_FIXED_GENERATED_AT,
        )
        .to_dict()
    )

    assert API_CONTRACT_ROOT in payload["boundary"]["source_paths"]
    assert API_CONTRACT_ROOT in payload["index"]["section_authority_trace"]["boundary"]
    for proof_path in NON_AUTHORITY_PROOF_PATHS:
        assert proof_path not in payload["boundary"]["source_paths"]
        assert proof_path not in payload["governance"]["source_paths"]


def test_evidence_pack_blocks_sensitive_values_and_uses_repo_relative_authority_paths() -> (
    None
):
    payload = (
        AiDebugEvidenceCollector()
        .collect(
            report_id="report-check",
            generated_at=_FIXED_GENERATED_AT,
        )
        .to_dict()
    )
    rendered = json.dumps(payload, ensure_ascii=False)
    family = payload["boundary"]["representative_families"][0]

    assert family["manifest_path"].startswith("tests/fixtures/protocol_replay/")
    assert not family["manifest_path"].startswith("/")
    assert family["authority_path"].startswith("tests/fixtures/")
    assert "password_hash" not in rendered
    assert "should-not-leak" not in rendered
    assert "03ab5ccd7c111111" not in rendered
    assert "03ab5ccd7c999999" not in rendered


def test_evidence_pack_surfaces_remaining_family_failure_and_drift_story() -> None:
    payload = (
        AiDebugEvidenceCollector(
            protocol_driver=_RepresentativeFailureDriftDriver(),
        )
        .collect(
            report_id="remaining-family-story",
            generated_at=_FIXED_GENERATED_AT,
        )
        .to_dict()
    )
    representative_story = payload["replay"]["summary"]["representative_failure_drift"]

    assert representative_story["remaining_family_channels"] == ["rest", "mqtt"]
    assert [
        scenario["family"]
        for scenario in representative_story["remaining_family_representatives"]
    ] == ["rest.schedule-json", "mqtt.message-envelope"]
    assert [
        scenario["family"] for scenario in representative_story["error_scenarios"]
    ] == ["rest.schedule-json"]
    assert representative_story["error_scenarios"][0]["error_category"] == "protocol"
    assert representative_story["error_scenarios"][0]["error_type"] == "ValueError"
    assert representative_story["error_scenarios"][0]["failure_summary"] == {
        "failure_category": "protocol",
        "failure_origin": "protocol.replay",
        "handling_policy": "inspect",
        "error_type": "ValueError",
    }
    assert [
        scenario["family"] for scenario in representative_story["drift_scenarios"]
    ] == ["mqtt.message-envelope"]
