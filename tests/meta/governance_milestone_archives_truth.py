"""Milestone-archive authority and latest-pointer truth guards."""
from __future__ import annotations

from .governance_contract_helpers import (
    _ROOT,
    _assert_latest_archived_route_truth,
    _assert_public_docs_hide_internal_route_story,
    assert_runbook_points_to_latest_evidence,
)
from .governance_current_truth import LATEST_ARCHIVED_EVIDENCE_FILENAME


def test_governance_truth_registers_v1_1_closeout_assets() -> None:
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "runtime telemetry exporter family" in authority_text
    assert "v1.1 closeout evidence index" in authority_text
    assert "7 / 7.5 / 15 / 16 / 17" in verification_text
    assert "V1_1_EVIDENCE_INDEX.md" in authority_text
    assert "## Phase 07.5 Residual Delta" in residual_text
    assert "de-scope" in residual_text
    assert "## Phase 07.5 Status Update" in kill_text

def test_governance_truth_registers_v1_2_closeout_assets() -> None:
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(
        encoding="utf-8"
    )

    assert "V1_2_EVIDENCE_INDEX.md" in authority_text
    assert "## Phase 21 Replay / Exception Taxonomy Contract" in verification_text
    assert "## Phase 24 Final Audit / Archive-Ready / Handoff Contract" in verification_text
    assert "## Phase 24 Final Audit Disposition" in residual_text
    assert "## Phase 24 Status Update" in kill_text
    assert "## v1.2 Host-Neutral Core & Replay Completion" in milestones_text

def test_governance_truth_registers_v1_5_closeout_assets() -> None:
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    public_text = (
        _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
    ).read_text(encoding="utf-8")
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(encoding="utf-8")

    assert "V1_5_EVIDENCE_INDEX.md" in authority_text
    assert "v1.5-MILESTONE-AUDIT.md" in authority_text
    assert "V1_5_EVIDENCE_INDEX.md" in public_text
    assert "## v1.5 Governance Truth Consolidation & Control-Surface Finalization" in milestones_text

def test_governance_truth_registers_v1_6_closeout_assets() -> None:
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    public_text = (
        _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
    ).read_text(encoding="utf-8")
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(encoding="utf-8")

    assert "V1_6_EVIDENCE_INDEX.md" in authority_text
    assert "v1.6-MILESTONE-AUDIT.md" in authority_text
    assert "V1_6_EVIDENCE_INDEX.md" in public_text
    assert "## v1.6 Delivery Trust Hardening, Runtime Boundary Decoupling & Maintainability Closure" in milestones_text

def test_governance_truth_registers_v1_14_archive_lineage() -> None:
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    public_text = (
        _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
    ).read_text(encoding="utf-8")
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(encoding="utf-8")

    assert "V1_14_EVIDENCE_INDEX.md" in authority_text
    assert "v1.14-MILESTONE-AUDIT.md" in authority_text
    assert "V1_14_EVIDENCE_INDEX.md" in public_text
    assert "## v1.13 Tooling Truth Decomposition, Formal-Home Slimming & Naming/Discoverability Convergence" in milestones_text
    assert "## v1.14 Governance Truth Realignment, Typed Runtime Access & Final Hidden-Root Closure" in milestones_text
    assert ".planning/reviews/V1_14_EVIDENCE_INDEX.md" in milestones_text

def test_governance_truth_registers_v1_27_latest_archive_pointer() -> None:
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    public_text = (
        _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
    ).read_text(encoding="utf-8")
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    docs_text = (_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    runbook_text = (_ROOT / "docs" / "MAINTAINER_RELEASE_RUNBOOK.md").read_text(
        encoding="utf-8"
    )

    assert "V1_19_EVIDENCE_INDEX.md" in authority_text
    assert "V1_20_EVIDENCE_INDEX.md" in authority_text
    assert "V1_21_EVIDENCE_INDEX.md" in authority_text
    assert "V1_22_EVIDENCE_INDEX.md" in authority_text
    assert "V1_23_EVIDENCE_INDEX.md" in authority_text
    assert "V1_24_EVIDENCE_INDEX.md" in authority_text
    assert "V1_25_EVIDENCE_INDEX.md" in authority_text
    assert "V1_27_EVIDENCE_INDEX.md" in authority_text
    assert "v1.24-MILESTONE-AUDIT.md" in authority_text
    assert "v1.25-MILESTONE-AUDIT.md" in authority_text
    assert "v1.27-MILESTONE-AUDIT.md" in authority_text
    assert "V1_24_EVIDENCE_INDEX.md" in public_text
    assert "V1_25_EVIDENCE_INDEX.md" in public_text
    assert "V1_27_EVIDENCE_INDEX.md" in public_text
    assert "## v1.23 Repository-Wide Terminal Code Audit, Residual Eradication & Closeout Truth Freeze" in milestones_text
    assert "## v1.24 Runtime Boundary Tightening, Tooling Kernel Decoupling & Open-Source Entry Convergence" in milestones_text
    assert "## v1.25 Hotspot Inward Decomposition, Typed Boundary Hardening & Redaction Convergence" in milestones_text
    assert "## v1.27 Final Carry-Forward Eradication & Route Reactivation" in milestones_text
    assert ".planning/reviews/V1_27_EVIDENCE_INDEX.md" in milestones_text
    _assert_public_docs_hide_internal_route_story(docs_text)
    assert_runbook_points_to_latest_evidence(
        runbook_text,
        LATEST_ARCHIVED_EVIDENCE_FILENAME,
        deprecated=("V1_6_EVIDENCE_INDEX.md",),
    )
    _assert_latest_archived_route_truth(project_text, roadmap_text, state_text)
