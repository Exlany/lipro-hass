"""Focused guards for Phase 88 governance/evidence freeze and zero-active posture."""

from __future__ import annotations

from .governance_contract_helpers import _ROOT
from .governance_promoted_assets import _assert_exact_promoted_phase_assets


def _section(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    return text[start_index:end_index]


def test_phase88_promoted_assets_manifest_matches_v123_closeout_inputs() -> None:
    _assert_exact_promoted_phase_assets(
        "85-terminal-audit-refresh-and-residual-routing",
        "85-01-SUMMARY.md",
        "85-02-SUMMARY.md",
        "85-03-SUMMARY.md",
    )
    _assert_exact_promoted_phase_assets(
        "86-production-residual-eradication-and-boundary-re-tightening",
        "86-01-SUMMARY.md",
        "86-02-SUMMARY.md",
        "86-03-SUMMARY.md",
        "86-04-SUMMARY.md",
        "86-VALIDATION.md",
    )
    _assert_exact_promoted_phase_assets(
        "87-assurance-hotspot-decomposition-and-no-regrowth-guards",
        "87-01-SUMMARY.md",
        "87-02-SUMMARY.md",
        "87-03-SUMMARY.md",
        "87-04-SUMMARY.md",
    )

    audit_text = (_ROOT / ".planning" / "reviews" / "V1_23_TERMINAL_AUDIT.md").read_text(
        encoding="utf-8"
    )
    assert "Historical review artifact for `AUD-04` / `GOV-62`" in audit_text
    assert "Historical route snapshot:" in audit_text
    assert ".planning/reviews/{PROMOTED_PHASE_ASSETS,RESIDUAL_LEDGER,KILL_LIST}.md" in audit_text


def test_phase88_zero_active_residual_and_delete_gate_posture_is_explicit() -> None:
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    active_section = _section(
        residual_text,
        "## Active Residual Families",
        "## Phase 85 Audit-Routed Carry-Forward",
    )
    phase85_kill_section = _section(
        kill_text,
        "## Phase 85 Routed Delete Gates",
        "## Deletion Gate",
    )

    assert active_section.count("_None currently registered._") == 1
    assert "Phase 88 freeze note" in active_section
    assert phase85_kill_section.count("_None currently registered._") == 1
    assert "Phase 88 freeze note" in phase85_kill_section
    assert (
        "| giant assurance carriers (`test_api_diagnostics_service.py`, `test_protocol_contract_matrix.py`, `test_mqtt_runtime.py`) | Assurance | closed in Phase 87 | Phase 87 |"
        in residual_text
    )
    assert (
        "| giant assurance carriers (`test_api_diagnostics_service.py`, `test_protocol_contract_matrix.py`, `test_mqtt_runtime.py`) | Assurance | route next | Phase 87 |"
        not in residual_text
    )


def test_phase88_public_surface_docs_and_verification_truth_freeze_the_same_story() -> None:
    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(
        encoding="utf-8"
    )
    dev_text = (_ROOT / "docs" / "architecture_archive.md").read_text(
        encoding="utf-8"
    )
    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    testing_text = (_ROOT / ".planning" / "codebase" / "TESTING.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 88 Governance Freeze Notes" in public_text
    assert "`v1.23` archived baseline promotion" in dev_text
    assert "## Phase 88 Governance Sync / Quality Proof / Milestone Freeze" in verification_text
    for token in (
        ".planning/reviews/PROMOTED_PHASE_ASSETS.md",
        "tests/meta/test_phase88_governance_quality_freeze_guards.py",
        "$gsd-complete-milestone v1.23",
        "$gsd-new-milestone",
        "zero orphan residuals",
    ):
        assert token in verification_text
    assert "tests/meta/test_phase88_governance_quality_freeze_guards.py" in file_matrix_text
    assert "focused guard home for phase-88 governance/evidence freeze" in file_matrix_text
    assert "tests/meta/test_phase88_governance_quality_freeze_guards.py" in testing_text
