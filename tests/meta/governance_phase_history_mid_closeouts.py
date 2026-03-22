"""Mid-milestone governance closeout execution evidence guards."""

from __future__ import annotations

from .test_governance_closeout_guards import (
    _assert_project_allows_post_v1_4_next_step,
    _assert_promoted_phase_assets,
    _assert_state_keeps_forward_progress_commands,
    _assert_state_reflects_post_v1_4_continuation,
)
from .test_governance_guards import _ROOT, _assert_current_mode_tracks_phase_lifecycle


def test_phase_34_execution_evidence_is_consistent() -> None:
    _assert_promoted_phase_assets(
        "34-continuity-and-hard-release-gates",
        "34-SUMMARY.md",
        "34-VERIFICATION.md",
    )

    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "34-continuity-and-hard-release-gates"
    )
    verification_text = (phase_root / "34-VERIFICATION.md").read_text(encoding="utf-8")
    summary_text = (phase_root / "34-SUMMARY.md").read_text(encoding="utf-8")

    assert "# Phase 34 Verification" in verification_text
    assert "status: passed" in verification_text
    assert "GOV-29" in verification_text
    assert "QLT-08" in verification_text
    assert "tagged `CodeQL` gate" in verification_text
    assert "cosign" in verification_text

    assert "phase: 34" in summary_text
    assert "status: passed" in summary_text
    assert "`34-01`" in summary_text
    assert "`34-02`" in summary_text
    assert "`34-03`" in summary_text


def test_phase_35_execution_evidence_is_consistent() -> None:
    _assert_promoted_phase_assets(
        "35-protocol-hotspot-final-slimming",
        "35-SUMMARY.md",
        "35-VERIFICATION.md",
    )

    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "35-protocol-hotspot-final-slimming"
    )
    verification_text = (phase_root / "35-VERIFICATION.md").read_text(encoding="utf-8")
    summary_text = (phase_root / "35-SUMMARY.md").read_text(encoding="utf-8")

    assert "# Phase 35 Verification" in verification_text
    assert "RestTransportExecutor" in verification_text
    assert "phase: 35" in summary_text


def test_phase_44_execution_evidence_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    docs_text = (_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "44-governance-asset-pruning-and-terminology-convergence"
    )
    summary_text = (phase_root / "44-SUMMARY.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "44-VERIFICATION.md").read_text(
        encoding="utf-8"
    )

    _assert_promoted_phase_assets(
        "44-governance-asset-pruning-and-terminology-convergence",
        "44-SUMMARY.md",
        "44-VERIFICATION.md",
    )

    assert "### Phase 44: Governance asset pruning and terminology convergence" in roadmap_text
    assert "**Status**: Complete (`2026-03-20`)" in roadmap_text
    assert "**Plans**: 4/4 complete" in roadmap_text
    for req_id in ("GOV-35", "RES-11", "DOC-04"):
        assert f"| {req_id} | Phase 44 | Completed |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)
    assert "## Archived Milestone (v1.6)" in project_text
    _assert_project_allows_post_v1_4_next_step(project_text)
    assert ".planning/reviews/V1_6_EVIDENCE_INDEX.md" in project_text
    assert "Public Fast Path" in docs_text
    assert "Bilingual Boundary" in docs_text
    assert "tests/meta/test_governance_release_contract.py" in file_matrix_text
    assert "toolchain + docs navigation + terminology truth guard home" in file_matrix_text
    assert "## Phase 44 Residual Delta" in residual_text
    assert "## Phase 44 Status Update" in kill_text
    assert "phase: 44" in summary_text
    assert "status: passed" in summary_text
    assert "44-01" in summary_text
    assert "# Phase 44 Verification" in verification_text
    assert "status: passed" in verification_text
    assert "Contributor Fast Path" in verification_text


def test_phase_45_execution_evidence_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    verification_matrix_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "45-hotspot-decomposition-and-typed-failure-semantics"
    )
    summary_text = (phase_root / "45-SUMMARY.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "45-VERIFICATION.md").read_text(
        encoding="utf-8"
    )

    _assert_promoted_phase_assets(
        "45-hotspot-decomposition-and-typed-failure-semantics",
        "45-SUMMARY.md",
        "45-VERIFICATION.md",
    )

    assert "### Phase 45: Hotspot decomposition and typed failure semantics" in roadmap_text
    assert "**Status**: Complete (`2026-03-20`)" in roadmap_text
    assert "**Plans**: 4/4 complete" in roadmap_text
    for req_id in ("HOT-11", "ERR-11", "TYP-10", "QLT-15"):
        assert f"| {req_id} | Phase 45 | Completed |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)
    assert "## Archived Milestone (v1.6)" in project_text
    _assert_project_allows_post_v1_4_next_step(project_text)
    assert ".planning/reviews/V1_6_EVIDENCE_INDEX.md" in project_text
    assert "16/16" in project_text
    assert "## Phase 45 Hotspot / Typed Failure / Benchmark Contract" in verification_matrix_text
    assert "scripts/check_benchmark_baseline.py" in file_matrix_text
    assert "tests/meta/test_phase45_hotspot_budget_guards.py" in file_matrix_text
    assert "## Phase 45 Residual Delta" in residual_text
    assert "## Phase 45 Status Update" in kill_text
    assert "phase: 45" in summary_text
    assert "status: passed" in summary_text
    assert "45-04" in summary_text
    assert "# Phase 45 Verification" in verification_text
    assert "status: passed" in verification_text
    assert "HOT-11" in verification_text
