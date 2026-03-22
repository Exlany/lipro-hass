"""Planning and closeout governance phase-history regression coverage."""

from __future__ import annotations

import re

from .test_governance_closeout_guards import (
    _assert_project_allows_post_v1_4_next_step,
    _assert_promoted_phase_assets,
    _assert_state_keeps_forward_progress_commands,
    _assert_state_reflects_post_v1_4_continuation,
)
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

    _assert_promoted_phase_assets(
        "07.5-integration-governance-verification-closeout",
        "07.5-VALIDATION.md",
    )

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

    _assert_promoted_phase_assets(
        "08-ai-debug-evidence-pack",
        "08-VALIDATION.md",
        "08-VERIFICATION.md",
    )

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

    _assert_promoted_phase_assets(
        "15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through",
        "15-VALIDATION.md",
        "15-VERIFICATION.md",
    )

    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through"
    )
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
    assert re.search(r"milestone: v1\.\d+", state_text) is not None
    assert any(
        marker in state_text
        for marker in (
            "status: archived",
            "status: active",
            "archive promotion",
            "$gsd-execute-phase 40",
            "$gsd-plan-phase 42",
        )
    )
    assert "- `Phase 24` 已完成并于 2026-03-17 重新验证" in state_text
    assert "**Historical archive assets:**" in project_text
    assert "archive-ready" in project_text

    for artifact in (
        _ROOT / ".planning" / "reviews" / "V1_2_EVIDENCE_INDEX.md",
        _ROOT / ".planning" / "v1.2-MILESTONE-AUDIT.md",
        _ROOT / ".planning" / "v1.3-HANDOFF.md",
    ):
        assert artifact.exists()
    _assert_promoted_phase_assets(
        "21-replay-exception-taxonomy-hardening",
        "21-01-SUMMARY.md",
        "21-02-SUMMARY.md",
        "21-03-SUMMARY.md",
        "21-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "22-observability-surface-convergence-and-signal-exposure",
        "22-01-SUMMARY.md",
        "22-02-SUMMARY.md",
        "22-03-SUMMARY.md",
        "22-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "23-governance-convergence-contributor-docs-and-release-evidence-closure",
        "23-01-SUMMARY.md",
        "23-02-SUMMARY.md",
        "23-03-SUMMARY.md",
        "23-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "24-final-milestone-audit-archive-readiness-and-v1-3-handoff-prep",
        "24-01-SUMMARY.md",
        "24-02-SUMMARY.md",
        "24-03-SUMMARY.md",
        "24-04-SUMMARY.md",
        "24-05-SUMMARY.md",
        "24-VERIFICATION.md",
    )


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

def test_phase_51_execution_evidence_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")

    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening"
    )
    summary_text = (phase_root / "51-SUMMARY.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "51-VERIFICATION.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "51-VALIDATION.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening",
        "51-SUMMARY.md",
        "51-VERIFICATION.md",
    )

    assert "### Phase 51: Continuity automation, governance-registry projection, and release rehearsal hardening" in roadmap_text
    assert "**Status**: Complete (`2026-03-21`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "**Promoted closeout package**: `51-SUMMARY.md`, `51-VERIFICATION.md`" in roadmap_text
    for req_id in ("GOV-38", "GOV-39", "QLT-18"):
        assert f"| {req_id} | Phase 51 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)
    assert "## Planned Milestone (v1.8)" in project_text
    assert "52-SUMMARY.md" in project_text
    assert "phase: 51" in summary_text
    assert "status: passed" in summary_text
    assert "51-03" in summary_text
    assert "# Phase 51 Verification" in verification_text
    assert "status: passed" in verification_text
    assert "GOV-38" in verification_text
    assert "status: passed" in validation_text
    assert "✅ passed" in validation_text

def test_phase_52_execution_evidence_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")

    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "52-protocol-root-second-round-slimming-and-request-policy-isolation"
    )
    summary_text = (phase_root / "52-SUMMARY.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "52-VERIFICATION.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "52-VALIDATION.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "52-protocol-root-second-round-slimming-and-request-policy-isolation",
        "52-SUMMARY.md",
        "52-VERIFICATION.md",
    )

    assert "### Phase 52: Protocol-root second-round slimming and request-policy isolation" in roadmap_text
    assert "**Status**: Complete (`2026-03-21`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "**Promoted closeout package**: `52-SUMMARY.md`, `52-VERIFICATION.md`" in roadmap_text
    assert "| ARC-08 | Phase 52 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)
    assert "## Planned Milestone (v1.8)" in project_text
    assert "$gsd-new-milestone" in project_text
    assert "phase: 52" in summary_text
    assert "status: passed" in summary_text
    assert "52-03" in summary_text
    assert "# Phase 52 Verification" in verification_text
    assert "status: passed" in verification_text
    assert "ARC-08" in verification_text
    assert "status: passed" in validation_text
    assert "✅ passed" in validation_text


def test_phase_53_execution_evidence_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")

    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "53-runtime-and-entry-root-second-round-throttling"
    )
    summary_text = (phase_root / "53-SUMMARY.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "53-VERIFICATION.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "53-VALIDATION.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "53-runtime-and-entry-root-second-round-throttling",
        "53-SUMMARY.md",
        "53-VERIFICATION.md",
    )

    assert "### Phase 53: Runtime and entry-root second-round throttling" in roadmap_text
    assert "**Status**: Complete (`2026-03-21`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "**Promoted closeout package**: `53-SUMMARY.md`, `53-VERIFICATION.md`" in roadmap_text
    assert "| HOT-12 | Phase 53 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)
    assert "## Planned Milestone (v1.8)" in project_text
    assert "53-SUMMARY.md" in project_text
    assert "phase: 53" in summary_text
    assert "status: passed" in summary_text
    assert "53-03" in summary_text
    assert "# Phase 53 Verification" in verification_text
    assert "status: passed" in verification_text
    assert "HOT-12" in verification_text
    assert "status: passed" in validation_text
    assert "Approval:" in validation_text


def test_phase_54_execution_evidence_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")

    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families"
    )
    summary_text = (phase_root / "54-SUMMARY.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "54-VERIFICATION.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "54-VALIDATION.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families",
        "54-SUMMARY.md",
        "54-VERIFICATION.md",
    )

    assert "### Phase 54: Helper-hotspot formalization for anonymous-share and diagnostics helper families" in roadmap_text
    assert "**Status**: Complete (`2026-03-21`)" in roadmap_text
    assert "**Plans**: 4/4 complete" in roadmap_text
    assert "**Promoted closeout package**: `54-SUMMARY.md`, `54-VERIFICATION.md`" in roadmap_text
    assert "| HOT-13 | Phase 54 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)
    assert "## Planned Milestone (v1.8)" in project_text
    assert "54-SUMMARY.md" in project_text
    assert "phase: 54" in summary_text
    assert "status: passed" in summary_text
    assert "54-04" in summary_text
    assert "# Phase 54 Verification" in verification_text
    assert "status: passed" in verification_text
    assert "HOT-13" in verification_text
    assert "status: passed" in validation_text
    assert "✅ passed" in validation_text


def test_phase_55_execution_evidence_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")

    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification"
    )
    summary_text = (phase_root / "55-SUMMARY.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "55-VERIFICATION.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "55-VALIDATION.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification",
        "55-SUMMARY.md",
        "55-VERIFICATION.md",
    )

    assert "### Phase 55: Mega-test topicization round 2 and repo-wide typing-metric stratification" in roadmap_text
    assert "**Status**: Complete (`2026-03-21`)" in roadmap_text
    assert "**Plans**: 5/5 complete" in roadmap_text
    assert "**Promoted closeout package**: `55-SUMMARY.md`, `55-VERIFICATION.md`" in roadmap_text
    assert "| TST-10 | Phase 55 | Complete |" in requirements_text
    assert "| TYP-13 | Phase 55 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)
    assert "## Planned Milestone (v1.8)" in project_text
    assert "55-SUMMARY.md" in project_text
    assert "phase: 55" in summary_text
    assert "status: passed" in summary_text
    assert "55-05" in summary_text
    assert "# Phase 55 Verification" in verification_text
    assert "status: passed" in verification_text
    assert "TST-10" in verification_text
    assert "TYP-13" in verification_text
    assert "status: passed" in validation_text
    assert "✅ passed" in validation_text



def test_phase_56_execution_evidence_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")

    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "56-shared-backoff-neutralization-and-cross-plane-retry-hygiene"
    )
    summary_text = (phase_root / "56-SUMMARY.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "56-VERIFICATION.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "56-VALIDATION.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "56-shared-backoff-neutralization-and-cross-plane-retry-hygiene",
        "56-SUMMARY.md",
        "56-VERIFICATION.md",
    )

    assert "### Phase 56: Shared backoff neutralization and cross-plane retry hygiene" in roadmap_text
    assert "**Status**: Complete (`2026-03-22`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "**Promoted closeout package**: `56-SUMMARY.md`, `56-VERIFICATION.md`" in roadmap_text
    assert "| RES-13 | Phase 56 | Complete |" in requirements_text
    assert "| ARC-09 | Phase 56 | Complete |" in requirements_text
    assert "| GOV-40 | Phase 56 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)
    assert "## Planned Milestone (v1.9)" in project_text
    assert "56-SUMMARY.md" in project_text
    assert "phase: 56" in summary_text
    assert "status: passed" in summary_text
    assert "56-03" in summary_text
    assert "# Phase 56 Verification" in verification_text
    assert "status: passed" in verification_text
    assert "RES-13" in verification_text
    assert "GOV-40" in verification_text
    assert "status: passed" in validation_text
    assert "Approval:" in validation_text


def test_phase_57_execution_evidence_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")

    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "57-command-result-typed-outcome-and-reason-code-hardening"
    )
    summary_text = (phase_root / "57-SUMMARY.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "57-VERIFICATION.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "57-VALIDATION.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "57-command-result-typed-outcome-and-reason-code-hardening",
        "57-SUMMARY.md",
        "57-VERIFICATION.md",
    )

    assert "### Phase 57: Command-result typed outcome and reason-code hardening" in roadmap_text
    assert "**Status**: Complete (`2026-03-22`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "**Promoted closeout package**: `57-SUMMARY.md`, `57-VERIFICATION.md`" in roadmap_text
    assert "| ERR-12 | Phase 57 | Complete |" in requirements_text
    assert "| TYP-14 | Phase 57 | Complete |" in requirements_text
    assert "| GOV-41 | Phase 57 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)
    assert "## Planned Milestone (v1.10)" in project_text
    assert "57-SUMMARY.md" in project_text
    assert "phase: 57" in summary_text
    assert "status: passed" in summary_text
    assert "57-03" in summary_text
    assert "# Phase 57 Verification" in verification_text
    assert "status: passed" in verification_text
    assert "ERR-12" in verification_text
    assert "GOV-41" in verification_text
    assert "status: passed" in validation_text
    assert "Approval:" in validation_text


def test_phase_58_execution_evidence_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")

    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "58-repository-audit-refresh-and-next-wave-routing"
    )
    summary_text = (phase_root / "58-SUMMARY.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "58-VERIFICATION.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "58-VALIDATION.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "58-repository-audit-refresh-and-next-wave-routing",
        "58-SUMMARY.md",
        "58-VERIFICATION.md",
    )

    assert "### Phase 58: Repository audit refresh and next-wave routing" in roadmap_text
    assert "**Status**: Complete (`2026-03-22`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "**Promoted closeout package**: `58-SUMMARY.md`, `58-VERIFICATION.md`" in roadmap_text
    assert "| AUD-03 | Phase 58 | Complete |" in requirements_text
    assert "| ARC-10 | Phase 58 | Complete |" in requirements_text
    assert "| OSS-06 | Phase 58 | Complete |" in requirements_text
    assert "| GOV-42 | Phase 58 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)
    assert "## Planned Milestone (v1.11)" in project_text
    assert "58-SUMMARY.md" in project_text
    assert "phase: 58" in summary_text
    assert "status: passed" in summary_text
    assert "58-03" in summary_text
    assert "# Phase 58 Verification" in verification_text
    assert "status: passed" in verification_text
    assert "AUD-03" in verification_text
    assert "GOV-42" in verification_text
    assert "status: planned" in validation_text or "status: passed" in validation_text
