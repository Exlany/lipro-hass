"""Closeout and promoted-asset topology guards for phase-history suites."""

from __future__ import annotations

from .conftest import _ROOT


def test_closed_service_execution_seam_is_not_active_governance_truth() -> None:
    agents_text = (_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    architecture_text = (
        _ROOT / ".planning" / "codebase" / "ARCHITECTURE.md"
    ).read_text(encoding="utf-8")
    structure_text = (_ROOT / ".planning" / "codebase" / "STRUCTURE.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "仍有 coordinator 私有 auth seam" not in agents_text
    assert (
        "formal service execution facade; private auth seam closed" in file_matrix_text
    )
    assert (
        "runtime-auth seam：`custom_components/lipro/services/execution.py`"
        not in architecture_text
    )
    assert "过渡性 runtime-auth seam" not in structure_text
    assert "Private runtime auth seam" in residual_text
    assert "active kill target" in kill_text

def test_phase_37_execution_evidence_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "37-test-topology-and-derived-truth-convergence"
    )
    validation_text = (phase_root / "37-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "37-VERIFICATION.md").read_text(encoding="utf-8")
    summary_text = (phase_root / "37-SUMMARY.md").read_text(encoding="utf-8")

    assert "status: passed" in validation_text
    assert "37-01-01" in validation_text and "✅ passed" in validation_text
    assert "# Phase 37 Verification" in verification_text
    assert "test_governance_phase_history*.py" in verification_text
    assert "phase: 37" in summary_text

def test_phase_38_execution_evidence_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "38-external-boundary-residual-retirement-and-quality-signal-hardening"
    )
    validation_text = (phase_root / "38-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "38-VERIFICATION.md").read_text(encoding="utf-8")
    summary_text = (phase_root / "38-SUMMARY.md").read_text(encoding="utf-8")

    assert "status: passed" in validation_text
    assert "38-01-01" in validation_text and "✅ passed" in validation_text
    assert "# Phase 38 Verification" in verification_text
    assert "advisory-with-artifact" in verification_text
    assert "phase: 38" in summary_text

def test_phase_asset_promotion_topology_stays_explicit() -> None:
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    manifest_text = (
        _ROOT / ".planning" / "reviews" / "PROMOTED_PHASE_ASSETS.md"
    ).read_text(encoding="utf-8")

    assert "promoted phase evidence allowlist" in authority_text
    assert ".planning/reviews/PROMOTED_PHASE_ASSETS.md" in verification_text
    assert "default_identity: execution-trace" in manifest_text
    assert "未被 allowlist 显式列出的 `*-SUMMARY.md`、`*-VERIFICATION.md`、`*-VALIDATION.md`" in manifest_text
