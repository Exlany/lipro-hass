"""Current-milestone governance execution evidence guards."""

from __future__ import annotations

from .conftest import _ROOT, _assert_current_mode_tracks_phase_lifecycle
from .test_governance_closeout_guards import (
    _assert_promoted_phase_assets,
    _assert_state_keeps_forward_progress_commands,
    _assert_state_reflects_post_v1_4_continuation,
)


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
    assert ("$gsd-new-milestone" in project_text or "$gsd-plan-phase 72" in project_text)
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

def test_phase_59_execution_evidence_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")

    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "59-verification-localization-and-governance-guard-topicization"
    )
    summary_text = (phase_root / "59-SUMMARY.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "59-VERIFICATION.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "59-VALIDATION.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "59-verification-localization-and-governance-guard-topicization",
        "59-SUMMARY.md",
        "59-VERIFICATION.md",
    )

    assert "### Phase 59: Verification localization and governance guard topicization" in roadmap_text
    assert "**Status**: Complete (`2026-03-22`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "**Promoted closeout package**: `59-SUMMARY.md`, `59-VERIFICATION.md`" in roadmap_text
    assert "| TST-11 | Phase 59 | Complete |" in requirements_text
    assert "| QLT-19 | Phase 59 | Complete |" in requirements_text
    assert "| GOV-43 | Phase 59 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)
    assert "## Archived Milestone (v1.12)" in project_text
    assert "59-SUMMARY.md" in project_text
    assert "phase: 59" in summary_text
    assert "status: passed" in summary_text
    assert "59-03" in summary_text
    assert "# Phase 59 Verification" in verification_text
    assert "status: passed" in verification_text
    assert "GOV-43" in verification_text
    assert "status: passed" in validation_text
    assert "✅ passed" in validation_text

