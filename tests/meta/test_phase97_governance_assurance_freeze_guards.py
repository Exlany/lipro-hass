"""Focused historical-closeout guards for Phase 97 governance and assurance freeze."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot

_ROOT = repo_root(Path(__file__))
_PROJECT = _ROOT / ".planning" / "PROJECT.md"
_ROADMAP = _ROOT / ".planning" / "ROADMAP.md"
_REQUIREMENTS = _ROOT / ".planning" / "REQUIREMENTS.md"
_STATE = _ROOT / ".planning" / "STATE.md"
_MILESTONES = _ROOT / ".planning" / "MILESTONES.md"
_VERIFICATION_MATRIX = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_TESTING = _ROOT / ".planning" / "codebase" / "TESTING.md"
_DEV_ARCH = _ROOT / "docs" / "developer_architecture.md"
_PHASE96_DIR = _ROOT / ".planning" / "phases" / "96-redaction-telemetry-and-anonymous-share-sanitizer-burndown"
_PHASE97_DIR = _ROOT / ".planning" / "phases" / "97-governance-open-source-contract-sync-and-assurance-freeze"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase97_closeout_bundle_stays_pull_only_after_v1_28_archived_handoff() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    dev_arch_text = _read(_DEV_ARCH)
    phase96_verification = _read(_PHASE96_DIR / "96-VERIFICATION.md")
    phase96_validation = _read(_PHASE96_DIR / "96-VALIDATION.md")
    phase97_verification = _read(_PHASE97_DIR / "97-VERIFICATION.md")
    phase97_validation = _read(_PHASE97_DIR / "97-VALIDATION.md")

    for text in (project_text, roadmap_text, requirements_text, milestones_text):
        assert "historical closeout route truth = `no active milestone route / latest archived baseline = v1.26`" in text

    assert "no active milestone route / latest archived baseline = v1.28" in state_text
    assert ".planning/v1.26-MILESTONE-AUDIT.md" in project_text
    assert ".planning/reviews/V1_26_EVIDENCE_INDEX.md" in project_text
    assert "archived / evidence-ready (2026-03-28)" in project_text
    assert "Phase 97 planning-ready" in phase96_verification
    assert "$gsd-plan-phase 97" in phase96_validation
    assert "# Phase 97 Verification" in phase97_verification
    assert "$gsd-complete-milestone v1.26" in phase97_validation
    assert "Phase 97 Governance / Assurance Freeze Note" in dev_arch_text


def test_phase97_file_testing_and_verification_maps_keep_historical_freeze_visible() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)

    assert "tests/meta/test_phase97_governance_assurance_freeze_guards.py" in file_matrix_text
    assert "focused closeout guard home for Phase 97 governance / assurance freeze" in file_matrix_text
    assert_testing_inventory_snapshot(testing_text)
    assert "## Phase 97 Governance / Open-Source Contract Sync and Assurance Freeze" in verification_text
