"""Archived phase-history execution evidence guards for v1.8-v1.12."""

from __future__ import annotations

from .conftest import _ROOT, _assert_current_mode_tracks_phase_lifecycle
from .test_governance_closeout_guards import (
    _assert_promoted_closeout_package,
    _assert_promoted_phase_assets,
    _assert_state_keeps_forward_progress_commands,
    _assert_state_reflects_post_v1_4_continuation,
)

_ROADMAP_TEXT = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
_REQUIREMENTS_TEXT = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
_STATE_TEXT = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
_PROJECT_TEXT = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")


def _load_phase_evidence(phase_dir_name: str, phase_number: str) -> tuple[str, str, str]:
    phase_root = _ROOT / ".planning" / "phases" / phase_dir_name
    return (
        (phase_root / f"{phase_number}-SUMMARY.md").read_text(encoding="utf-8"),
        (phase_root / f"{phase_number}-VERIFICATION.md").read_text(encoding="utf-8"),
        (phase_root / f"{phase_number}-VALIDATION.md").read_text(encoding="utf-8"),
    )


def _assert_phase_history_state_continuity(state_text: str) -> None:
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)


def _assert_phase_execution_markers(
    summary_text: str,
    verification_text: str,
    validation_text: str,
    *,
    phase_number: str,
    last_plan_marker: str,
    verification_markers: tuple[str, ...],
    validation_markers: tuple[str, ...] = (),
    validation_statuses: tuple[str, ...] = ("status: passed",),
) -> None:
    assert f"phase: {phase_number}" in summary_text
    assert "status: passed" in summary_text
    assert last_plan_marker in summary_text
    assert f"# Phase {phase_number} Verification" in verification_text
    assert "status: passed" in verification_text
    for marker in verification_markers:
        assert marker in verification_text
    assert any(status in validation_text for status in validation_statuses)
    for marker in validation_markers:
        assert marker in validation_text


def test_phase_51_execution_evidence_is_consistent() -> None:
    roadmap_text = _ROADMAP_TEXT
    requirements_text = _REQUIREMENTS_TEXT
    state_text = _STATE_TEXT
    project_text = _PROJECT_TEXT

    summary_text, verification_text, validation_text = _load_phase_evidence(
        "51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening",
        "51",
    )

    _assert_promoted_phase_assets(
        "51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening",
        "51-SUMMARY.md",
        "51-VERIFICATION.md",
    )

    assert "### Phase 51: Continuity automation, governance-registry projection, and release rehearsal hardening" in roadmap_text
    assert "**Status**: Complete (`2026-03-21`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    _assert_promoted_closeout_package(roadmap_text, "51-SUMMARY.md", "51-VERIFICATION.md")
    for req_id in ("GOV-38", "GOV-39", "QLT-18"):
        assert f"| {req_id} | Phase 51 | Complete |" in requirements_text
    _assert_phase_history_state_continuity(state_text)
    assert "## Planned Milestone (v1.8)" in project_text
    assert "52-SUMMARY.md" in project_text
    _assert_phase_execution_markers(
        summary_text,
        verification_text,
        validation_text,
        phase_number="51",
        last_plan_marker="51-03",
        verification_markers=("GOV-38",),
        validation_markers=("✅ passed",),
    )


def test_phase_52_execution_evidence_is_consistent() -> None:
    roadmap_text = _ROADMAP_TEXT
    requirements_text = _REQUIREMENTS_TEXT
    state_text = _STATE_TEXT
    project_text = _PROJECT_TEXT

    summary_text, verification_text, validation_text = _load_phase_evidence(
        "52-protocol-root-second-round-slimming-and-request-policy-isolation",
        "52",
    )

    _assert_promoted_phase_assets(
        "52-protocol-root-second-round-slimming-and-request-policy-isolation",
        "52-SUMMARY.md",
        "52-VERIFICATION.md",
    )

    assert "### Phase 52: Protocol-root second-round slimming and request-policy isolation" in roadmap_text
    assert "**Status**: Complete (`2026-03-21`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    _assert_promoted_closeout_package(roadmap_text, "52-SUMMARY.md", "52-VERIFICATION.md")
    assert "| ARC-08 | Phase 52 | Complete |" in requirements_text
    _assert_phase_history_state_continuity(state_text)
    assert "## Planned Milestone (v1.8)" in project_text
    _assert_phase_execution_markers(
        summary_text,
        verification_text,
        validation_text,
        phase_number="52",
        last_plan_marker="52-03",
        verification_markers=("ARC-08",),
        validation_markers=("✅ passed",),
    )


def test_phase_53_execution_evidence_is_consistent() -> None:
    roadmap_text = _ROADMAP_TEXT
    requirements_text = _REQUIREMENTS_TEXT
    state_text = _STATE_TEXT
    project_text = _PROJECT_TEXT

    summary_text, verification_text, validation_text = _load_phase_evidence(
        "53-runtime-and-entry-root-second-round-throttling",
        "53",
    )

    _assert_promoted_phase_assets(
        "53-runtime-and-entry-root-second-round-throttling",
        "53-SUMMARY.md",
        "53-VERIFICATION.md",
    )

    assert "### Phase 53: Runtime and entry-root second-round throttling" in roadmap_text
    assert "**Status**: Complete (`2026-03-21`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    _assert_promoted_closeout_package(roadmap_text, "53-SUMMARY.md", "53-VERIFICATION.md")
    assert "| HOT-12 | Phase 53 | Complete |" in requirements_text
    _assert_phase_history_state_continuity(state_text)
    assert "## Planned Milestone (v1.8)" in project_text
    assert "53-SUMMARY.md" in project_text
    _assert_phase_execution_markers(
        summary_text,
        verification_text,
        validation_text,
        phase_number="53",
        last_plan_marker="53-03",
        verification_markers=("HOT-12",),
        validation_markers=("Approval:",),
    )


def test_phase_54_execution_evidence_is_consistent() -> None:
    roadmap_text = _ROADMAP_TEXT
    requirements_text = _REQUIREMENTS_TEXT
    state_text = _STATE_TEXT
    project_text = _PROJECT_TEXT

    summary_text, verification_text, validation_text = _load_phase_evidence(
        "54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families",
        "54",
    )

    _assert_promoted_phase_assets(
        "54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families",
        "54-SUMMARY.md",
        "54-VERIFICATION.md",
    )

    assert "### Phase 54: Helper-hotspot formalization for anonymous-share and diagnostics helper families" in roadmap_text
    assert "**Status**: Complete (`2026-03-21`)" in roadmap_text
    assert "**Plans**: 4/4 complete" in roadmap_text
    _assert_promoted_closeout_package(roadmap_text, "54-SUMMARY.md", "54-VERIFICATION.md")
    assert "| HOT-13 | Phase 54 | Complete |" in requirements_text
    _assert_phase_history_state_continuity(state_text)
    assert "## Planned Milestone (v1.8)" in project_text
    assert "54-SUMMARY.md" in project_text
    _assert_phase_execution_markers(
        summary_text,
        verification_text,
        validation_text,
        phase_number="54",
        last_plan_marker="54-04",
        verification_markers=("HOT-13",),
        validation_markers=("✅ passed",),
    )


def test_phase_55_execution_evidence_is_consistent() -> None:
    roadmap_text = _ROADMAP_TEXT
    requirements_text = _REQUIREMENTS_TEXT
    state_text = _STATE_TEXT
    project_text = _PROJECT_TEXT

    summary_text, verification_text, validation_text = _load_phase_evidence(
        "55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification",
        "55",
    )

    _assert_promoted_phase_assets(
        "55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification",
        "55-SUMMARY.md",
        "55-VERIFICATION.md",
    )

    assert "### Phase 55: Mega-test topicization round 2 and repo-wide typing-metric stratification" in roadmap_text
    assert "**Status**: Complete (`2026-03-21`)" in roadmap_text
    assert "**Plans**: 5/5 complete" in roadmap_text
    _assert_promoted_closeout_package(roadmap_text, "55-SUMMARY.md", "55-VERIFICATION.md")
    assert "| TST-10 | Phase 55 | Complete |" in requirements_text
    assert "| TYP-13 | Phase 55 | Complete |" in requirements_text
    _assert_phase_history_state_continuity(state_text)
    assert "## Planned Milestone (v1.8)" in project_text
    assert "55-SUMMARY.md" in project_text
    _assert_phase_execution_markers(
        summary_text,
        verification_text,
        validation_text,
        phase_number="55",
        last_plan_marker="55-05",
        verification_markers=("TST-10", "TYP-13"),
        validation_markers=("✅ passed",),
    )


def test_phase_56_execution_evidence_is_consistent() -> None:
    roadmap_text = _ROADMAP_TEXT
    requirements_text = _REQUIREMENTS_TEXT
    state_text = _STATE_TEXT
    project_text = _PROJECT_TEXT

    summary_text, verification_text, validation_text = _load_phase_evidence(
        "56-shared-backoff-neutralization-and-cross-plane-retry-hygiene",
        "56",
    )

    _assert_promoted_phase_assets(
        "56-shared-backoff-neutralization-and-cross-plane-retry-hygiene",
        "56-SUMMARY.md",
        "56-VERIFICATION.md",
    )

    assert "### Phase 56: Shared backoff neutralization and cross-plane retry hygiene" in roadmap_text
    assert "**Status**: Complete (`2026-03-22`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    _assert_promoted_closeout_package(roadmap_text, "56-SUMMARY.md", "56-VERIFICATION.md")
    assert "| RES-13 | Phase 56 | Complete |" in requirements_text
    assert "| ARC-09 | Phase 56 | Complete |" in requirements_text
    assert "| GOV-40 | Phase 56 | Complete |" in requirements_text
    _assert_phase_history_state_continuity(state_text)
    assert "## Planned Milestone (v1.9)" in project_text
    assert "56-SUMMARY.md" in project_text
    _assert_phase_execution_markers(
        summary_text,
        verification_text,
        validation_text,
        phase_number="56",
        last_plan_marker="56-03",
        verification_markers=("RES-13", "GOV-40"),
        validation_markers=("Approval:",),
    )


def test_phase_57_execution_evidence_is_consistent() -> None:
    roadmap_text = _ROADMAP_TEXT
    requirements_text = _REQUIREMENTS_TEXT
    state_text = _STATE_TEXT
    project_text = _PROJECT_TEXT

    summary_text, verification_text, validation_text = _load_phase_evidence(
        "57-command-result-typed-outcome-and-reason-code-hardening",
        "57",
    )

    _assert_promoted_phase_assets(
        "57-command-result-typed-outcome-and-reason-code-hardening",
        "57-SUMMARY.md",
        "57-VERIFICATION.md",
    )

    assert "### Phase 57: Command-result typed outcome and reason-code hardening" in roadmap_text
    assert "**Status**: Complete (`2026-03-22`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    _assert_promoted_closeout_package(roadmap_text, "57-SUMMARY.md", "57-VERIFICATION.md")
    assert "| ERR-12 | Phase 57 | Complete |" in requirements_text
    assert "| TYP-14 | Phase 57 | Complete |" in requirements_text
    assert "| GOV-41 | Phase 57 | Complete |" in requirements_text
    _assert_phase_history_state_continuity(state_text)
    assert "## Planned Milestone (v1.10)" in project_text
    assert "57-SUMMARY.md" in project_text
    _assert_phase_execution_markers(
        summary_text,
        verification_text,
        validation_text,
        phase_number="57",
        last_plan_marker="57-03",
        verification_markers=("ERR-12", "GOV-41"),
        validation_markers=("Approval:",),
    )


def test_phase_58_execution_evidence_is_consistent() -> None:
    roadmap_text = _ROADMAP_TEXT
    requirements_text = _REQUIREMENTS_TEXT
    state_text = _STATE_TEXT
    project_text = _PROJECT_TEXT

    summary_text, verification_text, validation_text = _load_phase_evidence(
        "58-repository-audit-refresh-and-next-wave-routing",
        "58",
    )

    _assert_promoted_phase_assets(
        "58-repository-audit-refresh-and-next-wave-routing",
        "58-SUMMARY.md",
        "58-VERIFICATION.md",
    )

    assert "### Phase 58: Repository audit refresh and next-wave routing" in roadmap_text
    assert "**Status**: Complete (`2026-03-22`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    _assert_promoted_closeout_package(roadmap_text, "58-SUMMARY.md", "58-VERIFICATION.md")
    assert "| AUD-03 | Phase 58 | Complete |" in requirements_text
    assert "| ARC-10 | Phase 58 | Complete |" in requirements_text
    assert "| OSS-06 | Phase 58 | Complete |" in requirements_text
    assert "| GOV-42 | Phase 58 | Complete |" in requirements_text
    _assert_phase_history_state_continuity(state_text)
    assert "## Planned Milestone (v1.11)" in project_text
    assert "58-SUMMARY.md" in project_text
    _assert_phase_execution_markers(
        summary_text,
        verification_text,
        validation_text,
        phase_number="58",
        last_plan_marker="58-03",
        verification_markers=("AUD-03", "GOV-42"),
        validation_statuses=("status: planned", "status: passed"),
    )

def test_phase_59_execution_evidence_is_consistent() -> None:
    roadmap_text = _ROADMAP_TEXT
    requirements_text = _REQUIREMENTS_TEXT
    state_text = _STATE_TEXT
    project_text = _PROJECT_TEXT

    summary_text, verification_text, validation_text = _load_phase_evidence(
        "59-verification-localization-and-governance-guard-topicization",
        "59",
    )

    _assert_promoted_phase_assets(
        "59-verification-localization-and-governance-guard-topicization",
        "59-SUMMARY.md",
        "59-VERIFICATION.md",
    )

    assert "### Phase 59: Verification localization and governance guard topicization" in roadmap_text
    assert "**Status**: Complete (`2026-03-22`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    _assert_promoted_closeout_package(roadmap_text, "59-SUMMARY.md", "59-VERIFICATION.md")
    assert "| TST-11 | Phase 59 | Complete |" in requirements_text
    assert "| QLT-19 | Phase 59 | Complete |" in requirements_text
    assert "| GOV-43 | Phase 59 | Complete |" in requirements_text
    _assert_phase_history_state_continuity(state_text)
    assert "## Archived Milestone (v1.12)" in project_text
    assert "59-SUMMARY.md" in project_text
    _assert_phase_execution_markers(
        summary_text,
        verification_text,
        validation_text,
        phase_number="59",
        last_plan_marker="59-03",
        verification_markers=("GOV-43",),
        validation_markers=("✅ passed",),
    )

