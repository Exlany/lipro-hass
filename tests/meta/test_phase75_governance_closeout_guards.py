"""Focused guards for Phase 75 governance archive truth."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_ROUTE,
    HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH,
    HISTORICAL_CLOSEOUT_ROUTE_TRUTH,
    LATEST_ARCHIVED_MILESTONE_STATUS,
    LATEST_ARCHIVED_PROJECT_HEADER,
)
from .governance_promoted_assets import _load_promoted_phase_assets

_ROOT = repo_root(Path(__file__))
_PHASE75_DIR = "75-access-mode-truth-closure-evidence-promotion-formalization-and-thin-adapter-typing-hardening"


def test_phase75_exit_contract_freezes_promoted_evidence_chain() -> None:
    verification_text = (_ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md").read_text(encoding="utf-8")
    audit_text = (_ROOT / ".planning" / "v1.20-MILESTONE-AUDIT.md").read_text(encoding="utf-8")
    promoted = _load_promoted_phase_assets()

    assert "## Phase 75 Exit Contract" in verification_text
    assert ".planning/reviews/PROMOTED_PHASE_ASSETS.md" in verification_text
    assert ".planning/reviews/V1_20_EVIDENCE_INDEX.md" in verification_text
    assert "v1.20-MILESTONE-AUDIT.md" in verification_text
    assert "75-VERIFICATION.md" in verification_text
    assert "75-VALIDATION.md" in verification_text

    for phase_dir_name, expected in {
        "72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement": {"72-01-SUMMARY.md", "72-02-SUMMARY.md", "72-03-SUMMARY.md", "72-04-SUMMARY.md", "72-VERIFICATION.md", "72-VALIDATION.md"},
        "73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization": {"73-01-SUMMARY.md", "73-02-SUMMARY.md", "73-03-SUMMARY.md", "73-04-SUMMARY.md", "73-VERIFICATION.md", "73-VALIDATION.md"},
        "74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout": {"74-01-SUMMARY.md", "74-02-SUMMARY.md", "74-03-SUMMARY.md", "74-04-SUMMARY.md", "74-VERIFICATION.md", "74-VALIDATION.md"},
    }.items():
        assert promoted[phase_dir_name] == expected
        for filename in expected:
            assert filename in audit_text


def test_phase75_archive_truth_stays_frozen_after_closeout() -> None:
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(
        encoding="utf-8"
    )
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    for text in (project_text, roadmap_text, state_text):
        assert CURRENT_ROUTE in text or LATEST_ARCHIVED_MILESTONE_STATUS in text

    assert "| GOV-56 | Phase 72, 74, 75 | Completed |" in requirements_text
    assert "| ARC-19 | Phase 72, 73, 75 | Completed |" in requirements_text
    assert "| TYP-21 | Phase 72, 73, 75 | Completed |" in requirements_text
    assert "| TST-22 | Phase 72, 73, 74, 75 | Completed |" in requirements_text
    assert "| QLT-30 | Phase 72, 73, 74, 75 | Completed |" in requirements_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in project_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in roadmap_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in state_text
    assert LATEST_ARCHIVED_PROJECT_HEADER in project_text
    assert "## Latest Archived Milestone" in roadmap_text
    assert HISTORICAL_CLOSEOUT_ROUTE_TRUTH in milestones_text
    assert HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH in milestones_text
    assert HISTORICAL_CLOSEOUT_ROUTE_TRUTH in roadmap_text
    assert HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH in roadmap_text
    assert HISTORICAL_CLOSEOUT_ROUTE_TRUTH in requirements_text
    assert HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH in requirements_text
    for text in (milestones_text, roadmap_text, requirements_text):
        assert "current governance state =" not in text
        assert "当前治理状态已切换为" not in text
        assert "当前治理状态现已切换为" not in text
        assert "live governance state" not in text
    assert _PHASE75_DIR in str(_ROOT / ".planning" / "phases" / _PHASE75_DIR)


def test_phase75_evidence_files_exist_without_promotion() -> None:
    phase_dir = _ROOT / ".planning" / "phases" / _PHASE75_DIR
    promoted = _load_promoted_phase_assets()

    for filename in (
        "75-01-SUMMARY.md",
        "75-02-SUMMARY.md",
        "75-03-SUMMARY.md",
        "75-04-SUMMARY.md",
        "75-VERIFICATION.md",
        "75-VALIDATION.md",
    ):
        assert (phase_dir / filename).exists()
        assert filename not in promoted.get(_PHASE75_DIR, frozenset())
