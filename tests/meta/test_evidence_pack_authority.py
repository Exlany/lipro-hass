"""Meta guards for AI debug evidence-pack authority and governance registration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.check_file_matrix import classify_path
from tests.harness.evidence_pack.collector import AiDebugEvidenceCollector
from tests.harness.evidence_pack.sources import (
    ALLOWED_FORMAL_SOURCE_PATHS,
    NON_AUTHORITY_PROOF_PATHS,
)
from tests.harness.protocol.replay_report import EXPLICIT_REPLAY_ASSURANCE_FAMILIES
from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_BLOCKED_KEYS = {
    "access_token",
    "access_key",
    "password",
    "password_hash",
    "phone",
    "phone_id",
    "refresh_access_key",
    "refresh_token",
    "secret",
    "token",
}


def _iter_keys(payload: Any):
    if isinstance(payload, dict):
        for key, value in payload.items():
            yield str(key)
            yield from _iter_keys(value)
    elif isinstance(payload, list):
        for item in payload:
            yield from _iter_keys(item)


def test_evidence_pack_only_emits_registered_formal_source_paths() -> None:
    payload = AiDebugEvidenceCollector().collect(
        report_id="authority-check",
        generated_at="2026-03-13T00:00:00Z",
    ).to_dict()
    allowed = set(ALLOWED_FORMAL_SOURCE_PATHS)

    for relative_path in allowed:
        assert (_ROOT / relative_path).exists(), relative_path
    for section in ("telemetry", "replay", "boundary", "governance"):
        assert set(payload[section]["source_paths"]).issubset(allowed)
    for sources in payload["index"]["section_authority_trace"].values():
        assert set(sources).issubset(allowed)
    assert [
        family["family"]
        for family in payload["boundary"]["remaining_family_projections"]
    ] == list(EXPLICIT_REPLAY_ASSURANCE_FAMILIES)
    for family in payload["boundary"]["remaining_family_projections"]:
        assert family["manifest_path"].startswith("tests/fixtures/protocol_replay/")
        assert family["authority_path"].startswith("tests/fixtures/")


def test_evidence_pack_governance_truth_registers_phase_8_assets() -> None:
    authority_text = (_ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md").read_text(encoding="utf-8")
    public_surface_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(encoding="utf-8")
    verification_text = (_ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md").read_text(encoding="utf-8")
    evidence_index_text = (_ROOT / ".planning" / "reviews" / "V1_1_EVIDENCE_INDEX.md").read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8")

    assert "AI debug evidence pack family" in authority_text
    assert "tests/harness/evidence_pack/*" in public_surface_text
    assert "scripts/export_ai_debug_evidence_pack.py" in public_surface_text
    assert "| `AID-*` |" in verification_text
    assert "| 8 |" in verification_text
    assert "AI debug evidence pack" in evidence_index_text
    assert "scripts/export_ai_debug_evidence_pack.py" in evidence_index_text
    assert "## Phase 08 Residual Delta" in residual_text


def test_headless_proof_assets_do_not_become_evidence_authority_sources() -> None:
    allowed = set(ALLOWED_FORMAL_SOURCE_PATHS)

    assert allowed.isdisjoint(NON_AUTHORITY_PROOF_PATHS)


def test_evidence_pack_redaction_contract_blocks_sensitive_key_names() -> None:
    payload = AiDebugEvidenceCollector().collect(
        report_id="redaction-check",
        generated_at="2026-03-13T00:00:00Z",
    ).to_dict()
    assert _BLOCKED_KEYS.isdisjoint({key.lower() for key in _iter_keys(payload)})


def test_file_matrix_classifier_registers_phase_8_assets() -> None:
    assert classify_path("tests/harness/evidence_pack/schema.py").owner_phase == "Phase 8"
    assert classify_path("tests/harness/evidence_pack/collector.py").owner_phase == "Phase 8"
    assert classify_path("tests/integration/test_ai_debug_evidence_pack.py").owner_phase == "Phase 8"
    assert classify_path("tests/meta/test_evidence_pack_authority.py").owner_phase == "Phase 8"
    assert classify_path("scripts/export_ai_debug_evidence_pack.py").owner_phase == "Phase 8"
