"""Planning and closeout governance phase-history regression coverage."""

from __future__ import annotations

from .test_governance_guards import (
    _ROOT,
    _assert_current_mode_tracks_phase_lifecycle,
    _assert_state_preserves_phase_17_closeout_history,
)


def test_phase_7_5_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    validation_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "07.5-integration-governance-verification-closeout"
        / "07.5-VALIDATION.md"
    ).read_text(encoding="utf-8")

    assert (
        "| 7.5 Governance & Verification | v1.1 | 2/2 | Complete | 2026-03-13 |"
        in roadmap_text
    )
    assert "| GOV-06 | Phase 7.5 | Complete |" in requirements_text
    assert "| GOV-07 | Phase 7.5 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "status: passed" in validation_text
    assert "- [x] `.planning/reviews/V1_1_EVIDENCE_INDEX.md`" in validation_text
    assert (
        "- [x] All tasks have automated verify or Wave 0 dependencies"
        in validation_text
    )


def test_phase_8_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    validation_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "08-ai-debug-evidence-pack"
        / "08-VALIDATION.md"
    ).read_text(encoding="utf-8")
    verification_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "08-ai-debug-evidence-pack"
        / "08-VERIFICATION.md"
    ).read_text(encoding="utf-8")

    assert (
        "| 8 AI Debug Evidence Pack | v1.1 | 2/2 | Complete | 2026-03-13 |"
        in roadmap_text
    )
    assert "| AID-01 | Phase 8 | Complete |" in requirements_text
    assert "| AID-02 | Phase 8 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "status: passed" in validation_text
    assert "nyquist_compliant: true" in validation_text
    assert "wave_0_complete: true" in validation_text
    assert "status: passed" in verification_text


def test_phase_15_execution_truth_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(
        encoding="utf-8"
    )
    architecture_policy_text = (
        _ROOT / ".planning" / "baseline" / "ARCHITECTURE_POLICY.md"
    ).read_text(encoding="utf-8")
    verification_matrix_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    prd_text = (phase_root / "15-PRD.md").read_text(encoding="utf-8")
    context_text = (phase_root / "15-CONTEXT.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "15-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "15-VERIFICATION.md").read_text(encoding="utf-8")

    assert (
        "### 10. Phase 15 支持反馈契约 / 治理真源修补 / 可维护性跟进已完成"
        in project_text
    )
    assert (
        "| 15 Support Feedback Contract Hardening, Governance Truth Repair & Maintainability Follow-Through | v1.1 | 5/5 | Complete | 2026-03-15 |"
        in roadmap_text
    )
    assert (
        "**Requirements**: [SPT-01, GOV-13, DOC-01, HOT-03, QLT-01, TYP-03, RES-01]"
        in roadmap_text
    )
    for req_id in (
        "SPT-01",
        "GOV-13",
        "DOC-01",
        "HOT-03",
        "QLT-01",
        "TYP-03",
        "RES-01",
    ):
        assert f"| {req_id} | Phase 15 | Complete |" in requirements_text
    _assert_state_preserves_phase_17_closeout_history(state_text)
    assert "2026.3.1" in prd_text
    assert "2026.3.1" in context_text
    assert "status: passed" in validation_text
    assert "status: passed" in verification_text
    assert "## Phase 15 Surface Closure Notes" in public_text
    assert "## Phase 15 Exit Contract" in verification_matrix_text
    assert "## Phase 15 Residual Delta" in residual_text
    assert "## Phase 15 Status Update" in kill_text
    assert "## Phase 15 Policy Follow-Through" in architecture_policy_text
    assert "custom_components/lipro/core/api/session_state.py" in file_matrix_text
    assert "RestSessionState formal REST session-state home" in file_matrix_text
    assert "custom_components/lipro/core/mqtt/transport.py" in file_matrix_text
    assert (
        "concrete MQTT transport home; package no-export keeps locality explicit"
        in file_matrix_text
    )

    for artifact_name in (
        "15-01-PLAN.md",
        "15-02-PLAN.md",
        "15-03-PLAN.md",
        "15-04-PLAN.md",
        "15-05-PLAN.md",
        "15-01-SUMMARY.md",
        "15-02-SUMMARY.md",
        "15-03-SUMMARY.md",
        "15-04-SUMMARY.md",
        "15-05-SUMMARY.md",
        "15-VALIDATION.md",
        "15-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()


def test_phase_21_to_24_execution_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")

    for heading in (
        "### Phase 21: Replay Coverage & Exception Taxonomy Hardening",
        "### Phase 22: Observability Surface Convergence & Signal Exposure",
        "### Phase 23: Governance convergence, contributor docs and release evidence closure",
        "### Phase 24: Final milestone audit, archive readiness and v1.3 handoff prep",
    ):
        assert heading in roadmap_text
    assert roadmap_text.count("**Status**: Complete (`2026-03-16`)") >= 3
    assert (
        "**Status**: Complete (`2026-03-17`, revalidated after reopen)" in roadmap_text
    )
    assert "**Plans**: 5/5 complete" in roadmap_text

    for req_id in ("SIM-04", "ERR-02", "OBS-03", "GOV-16", "GOV-17", "GOV-18"):
        assert f"| {req_id} | Phase" in requirements_text
        assert (
            f"| {req_id} | Phase" in requirements_text
            and "| Complete |" in requirements_text
        )
    assert "completed_phases: 7" in state_text
    assert "completed_plans: 24" in state_text
    assert "- `Phase 24` 已完成并于 2026-03-17 重新验证" in state_text
    assert "**Execution status:** `Phase 18-24` complete" in project_text
    assert "archive-ready / `v1.3` handoff-ready" in project_text

    assert (_ROOT / ".planning" / "phases" / "21-24-v1.2-closeout-strategy.md").exists()
    for artifact in (
        _ROOT / ".planning" / "reviews" / "V1_2_EVIDENCE_INDEX.md",
        _ROOT / ".planning" / "v1.2-MILESTONE-AUDIT.md",
        _ROOT / ".planning" / "v1.3-HANDOFF.md",
    ):
        assert artifact.exists()

    expected = {
        "21-replay-exception-taxonomy-hardening": [
            "21-CONTEXT.md",
            "21-RESEARCH.md",
            "21-VALIDATION.md",
            "21-01-PLAN.md",
            "21-02-PLAN.md",
            "21-03-PLAN.md",
            "21-01-SUMMARY.md",
            "21-02-SUMMARY.md",
            "21-03-SUMMARY.md",
            "21-VERIFICATION.md",
        ],
        "22-observability-surface-convergence-and-signal-exposure": [
            "22-CONTEXT.md",
            "22-RESEARCH.md",
            "22-VALIDATION.md",
            "22-01-PLAN.md",
            "22-02-PLAN.md",
            "22-03-PLAN.md",
            "22-01-SUMMARY.md",
            "22-02-SUMMARY.md",
            "22-03-SUMMARY.md",
            "22-VERIFICATION.md",
        ],
        "23-governance-convergence-contributor-docs-and-release-evidence-closure": [
            "23-CONTEXT.md",
            "23-RESEARCH.md",
            "23-VALIDATION.md",
            "23-01-PLAN.md",
            "23-02-PLAN.md",
            "23-03-PLAN.md",
            "23-04-PLAN.md",
            "23-05-PLAN.md",
            "23-06-PLAN.md",
            "23-07-PLAN.md",
            "23-08-PLAN.md",
            "23-01-SUMMARY.md",
            "23-02-SUMMARY.md",
            "23-03-SUMMARY.md",
            "23-04-SUMMARY.md",
            "23-05-SUMMARY.md",
            "23-06-SUMMARY.md",
            "23-07-SUMMARY.md",
            "23-08-SUMMARY.md",
            "23-AUDIT-CHECKLIST.md",
            "23-VERIFICATION.md",
        ],
        "24-final-milestone-audit-archive-readiness-and-v1-3-handoff-prep": [
            "24-CONTEXT.md",
            "24-RESEARCH.md",
            "24-VALIDATION.md",
            "24-01-PLAN.md",
            "24-02-PLAN.md",
            "24-03-PLAN.md",
            "24-01-SUMMARY.md",
            "24-02-SUMMARY.md",
            "24-03-SUMMARY.md",
            "24-VERIFICATION.md",
        ],
    }
    for phase_dir, artifacts in expected.items():
        phase_root = _ROOT / ".planning" / "phases" / phase_dir
        for artifact_name in artifacts:
            assert (phase_root / artifact_name).exists()


def test_phase_34_execution_evidence_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "34-continuity-and-hard-release-gates"
    )
    validation_text = (phase_root / "34-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "34-VERIFICATION.md").read_text(encoding="utf-8")
    summary_text = (phase_root / "34-SUMMARY.md").read_text(encoding="utf-8")

    assert "status: passed" in validation_text
    assert "nyquist_compliant: true" in validation_text
    assert "34-01-01" in validation_text and "✅ passed" in validation_text
    assert "34-02-01" in validation_text and "✅ passed" in validation_text
    assert "34-03-01" in validation_text and "✅ passed" in validation_text
    assert "**Approval:** complete" in validation_text

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
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "35-protocol-hotspot-final-slimming"
    )
    validation_text = (phase_root / "35-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "35-VERIFICATION.md").read_text(encoding="utf-8")
    summary_text = (phase_root / "35-SUMMARY.md").read_text(encoding="utf-8")

    assert "status: passed" in validation_text
    assert "35-01-01" in validation_text and "✅ passed" in validation_text
    assert "# Phase 35 Verification" in verification_text
    assert "RestTransportExecutor" in verification_text
    assert "phase: 35" in summary_text
