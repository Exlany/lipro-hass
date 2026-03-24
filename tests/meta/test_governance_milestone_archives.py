"""Governance guards for milestone archive snapshots and closeout indexes."""

from __future__ import annotations

from .test_governance_closeout_guards import _ROOT, _assert_promoted_phase_assets


def test_v1_1_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_1_EVIDENCE_INDEX.md"

    assert evidence_index.exists()
    _assert_promoted_phase_assets(
        "07.5-integration-governance-verification-closeout",
        "07.5-SUMMARY.md",
        "07.5-01-SUMMARY.md",
        "07.5-02-SUMMARY.md",
        "07.5-VERIFICATION.md",
    )

    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    assert "07.3-runtime-telemetry-exporter" in evidence_text
    assert "07.4-protocol-replay-simulator-harness" in evidence_text
    assert "Phase 8 Pull Boundary" in evidence_text


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


def test_v1_2_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_2_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.2-MILESTONE-AUDIT.md"
    handoff = _ROOT / ".planning" / "v1.3-HANDOFF.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert handoff.exists()
    _assert_promoted_phase_assets(
        "23-governance-convergence-contributor-docs-and-release-evidence-closure",
        "23-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "24-final-milestone-audit-archive-readiness-and-v1-3-handoff-prep",
        "24-VERIFICATION.md",
    )

    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    assert "21-VERIFICATION.md" in evidence_text
    assert "24-VERIFICATION.md" in evidence_text
    assert "archive-ready" in evidence_text
    assert "handoff-ready" in evidence_text


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


def test_milestone_archive_snapshots_exist_and_are_referenced() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(encoding="utf-8")

    archive_paths = (
        _ROOT / ".planning" / "milestones" / "v1.1-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.1-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.2-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.2-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.4-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.4-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.5-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.5-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.6-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.6-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.12-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.12-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.13-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.13-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.14-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.14-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.15-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.15-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.16-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.16-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.17-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.17-REQUIREMENTS.md",
    )

    for path in archive_paths:
        assert path.exists()

    for needle in (
        "v1.1-ROADMAP.md",
        "v1.1-REQUIREMENTS.md",
        "v1.2-ROADMAP.md",
        "v1.2-REQUIREMENTS.md",
        "v1.4-ROADMAP.md",
        "v1.4-REQUIREMENTS.md",
        "v1.5-ROADMAP.md",
        "v1.5-REQUIREMENTS.md",
        "v1.6-ROADMAP.md",
        "v1.6-REQUIREMENTS.md",
        "v1.12-ROADMAP.md",
        "v1.12-REQUIREMENTS.md",
        "v1.13-ROADMAP.md",
        "v1.13-REQUIREMENTS.md",
        "v1.14-ROADMAP.md",
        "v1.14-REQUIREMENTS.md",
        "v1.15-ROADMAP.md",
        "v1.15-REQUIREMENTS.md",
        "v1.16-ROADMAP.md",
        "v1.16-REQUIREMENTS.md",
        "v1.17-ROADMAP.md",
        "v1.17-REQUIREMENTS.md",
    ):
        assert needle in roadmap_text
        assert needle in requirements_text or needle in project_text or needle in milestones_text

    assert "v1.16-MILESTONE-AUDIT.md" in state_text
    assert "$gsd-new-milestone" in state_text
    assert "archived / evidence-ready" in milestones_text
    assert "archived snapshots created / handoff-ready" in milestones_text
    assert "revalidated 2026-03-17" in milestones_text
    assert ".planning/v1.4-MILESTONE-AUDIT.md" in milestones_text
    assert ".planning/v1.5-MILESTONE-AUDIT.md" in milestones_text
    assert "V1_4_EVIDENCE_INDEX.md" in milestones_text
    assert "V1_5_EVIDENCE_INDEX.md" in milestones_text
    assert ".planning/v1.5-MILESTONE-AUDIT.md" in milestones_text
    assert "V1_5_EVIDENCE_INDEX.md" in milestones_text

    v1_1_archive_text = (
        _ROOT / ".planning" / "milestones" / "v1.1-ROADMAP.md"
    ).read_text(encoding="utf-8")

    assert "待执行 milestone archival" not in v1_1_archive_text
    assert "当当前里程碑完成时，应能同时回答以下问题：" in project_text


def test_v1_5_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_5_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.5-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.5-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.5-REQUIREMENTS.md").exists()
    assert (
        _ROOT
        / ".planning"
        / "phases"
        / "40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification"
        / "40-VALIDATION.md"
    ).exists()
    _assert_promoted_phase_assets(
        "40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification",
        "40-SUMMARY.md",
        "40-VERIFICATION.md",
    )

    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    assert "40-VERIFICATION.md" in evidence_text
    assert "archive-ready / shipped" in evidence_text
    assert "V1_5_EVIDENCE_INDEX.md" in evidence_text


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


def test_v1_6_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_6_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.6-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.6-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.6-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "42-delivery-trust-gates-and-validation-hardening",
        "42-SUMMARY.md",
        "42-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "43-control-services-boundary-decoupling-and-typed-runtime-access",
        "43-SUMMARY.md",
        "43-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "44-governance-asset-pruning-and-terminology-convergence",
        "44-SUMMARY.md",
        "44-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "45-hotspot-decomposition-and-typed-failure-semantics",
        "45-SUMMARY.md",
        "45-VERIFICATION.md",
    )

    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    assert "42-VERIFICATION.md" in evidence_text
    assert "43-VERIFICATION.md" in evidence_text
    assert "44-VERIFICATION.md" in evidence_text
    assert "45-VERIFICATION.md" in evidence_text
    assert "archive-ready / shipped" in evidence_text
    assert "V1_6_EVIDENCE_INDEX.md" in evidence_text


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


def test_v1_14_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_14_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.14-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.14-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.14-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "63-governance-truth-realignment-typed-runtime-access-and-hidden-root-closure",
        "63-SUMMARY.md",
        "63-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "64-telemetry-typing-schedule-contracts-and-diagnostics-hotspot-slimming",
        "64-SUMMARY.md",
        "64-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure",
        "65-SUMMARY.md",
        "65-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening",
        "66-SUMMARY.md",
        "66-VERIFICATION.md",
    )

    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    assert "63-VERIFICATION.md" in evidence_text
    assert "64-VERIFICATION.md" in evidence_text
    assert "65-VERIFICATION.md" in evidence_text
    assert "66-VERIFICATION.md" in evidence_text
    assert "archived / evidence-ready" in evidence_text
    assert "V1_14_EVIDENCE_INDEX.md" in evidence_text


def test_v1_15_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_15_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.15-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.15-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.15-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "67-typed-contract-convergence-toolchain-hardening-and-mypy-closure",
        "67-SUMMARY.md",
        "67-VERIFICATION.md",
    )

    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    assert "67-SUMMARY.md" in evidence_text
    assert "67-VERIFICATION.md" in evidence_text
    assert "67-VALIDATION.md" in evidence_text
    assert "archived / evidence-ready" in evidence_text
    assert "V1_15_EVIDENCE_INDEX.md" in evidence_text


def test_v1_16_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_16_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.16-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.16-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.16-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening",
        "68-SUMMARY.md",
        "68-VERIFICATION.md",
    )

    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    assert "68-SUMMARY.md" in evidence_text
    assert "68-VERIFICATION.md" in evidence_text
    assert "68-VALIDATION.md" in evidence_text
    assert "carry-forward" in evidence_text
    assert "V1_16_EVIDENCE_INDEX.md" in evidence_text


def test_v1_17_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_17_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.17-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.17-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.17-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "69-residual-read-model-quality-balance-and-open-source-contract-closure",
        "69-SUMMARY.md",
        "69-VERIFICATION.md",
    )

    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    assert "69-SUMMARY.md" in evidence_text
    assert "69-VERIFICATION.md" in evidence_text
    assert "69-VALIDATION.md" in evidence_text
    assert "archived / evidence-ready" in evidence_text
    assert "V1_17_EVIDENCE_INDEX.md" in evidence_text


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


def test_governance_truth_registers_v1_17_latest_archive_pointer() -> None:
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    public_text = (
        _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
    ).read_text(encoding="utf-8")
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    docs_text = (_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    runbook_text = (_ROOT / "docs" / "MAINTAINER_RELEASE_RUNBOOK.md").read_text(
        encoding="utf-8"
    )

    assert "V1_16_EVIDENCE_INDEX.md" in authority_text
    assert "V1_17_EVIDENCE_INDEX.md" in authority_text
    assert "v1.17-MILESTONE-AUDIT.md" in authority_text
    assert "V1_17_EVIDENCE_INDEX.md" in public_text
    assert "## v1.16 Master Audit Follow-Through, Hotspot Finalization & Docs Contract Hardening" in milestones_text
    assert "## v1.17 Residual Formalization, Quality-Balance Hardening & Open-Source Contract Closure" in milestones_text
    assert ".planning/reviews/V1_17_EVIDENCE_INDEX.md" in milestones_text
    assert ".planning/reviews/V1_17_EVIDENCE_INDEX.md" in docs_text
    assert "当前无 active milestone route" in docs_text
    assert "v1.17 / Phase 69" not in docs_text
    assert "V1_17_EVIDENCE_INDEX.md" in runbook_text
    assert "$gsd-new-milestone" in project_text
    assert "$gsd-new-milestone" in state_text
    assert "No active milestone route" in project_text
    assert "**Current mode:** `v1.17 archived`" in state_text
