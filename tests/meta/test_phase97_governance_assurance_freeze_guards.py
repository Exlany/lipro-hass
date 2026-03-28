"""Focused closeout guards for Phase 97 governance and assurance freeze."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

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


def test_phase97_current_route_docs_and_closeout_bundles_align() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    verification_text = _read(_VERIFICATION_MATRIX)
    dev_arch_text = _read(_DEV_ARCH)
    phase96_verification = _read(_PHASE96_DIR / "96-VERIFICATION.md")
    phase96_validation = _read(_PHASE96_DIR / "96-VALIDATION.md")
    phase97_verification = _read(_PHASE97_DIR / "97-VERIFICATION.md")
    phase97_validation = _read(_PHASE97_DIR / "97-VALIDATION.md")

    for text in (project_text, roadmap_text, requirements_text, state_text, milestones_text, verification_text):
        assert "v1.26 active route / Phase 97 complete / latest archived baseline = v1.25" in text
        assert "$gsd-complete-milestone v1.26" in text

    assert "active / closeout-ready (2026-03-28)" in project_text
    assert "active / closeout-ready (2026-03-28)" in roadmap_text
    assert "active / closeout-ready (2026-03-28)" in requirements_text
    assert "active / closeout-ready (2026-03-28)" in state_text
    assert "active / closeout-ready (2026-03-28)" in milestones_text
    assert "Phase 97 planning-ready" in phase96_verification
    assert "$gsd-plan-phase 97" in phase96_validation
    assert "# Phase 97 Verification" in phase97_verification
    assert "$gsd-complete-milestone v1.26" in phase97_validation
    assert "Phase 97 Governance / Assurance Freeze Note" in dev_arch_text


def test_phase97_file_and_testing_maps_freeze_new_guard_footprint() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)

    assert "**Python files total:** 709" in file_matrix_text
    assert "tests/meta/test_phase96_sanitizer_burndown_guards.py" in file_matrix_text
    assert "tests/meta/test_phase97_governance_assurance_freeze_guards.py" in file_matrix_text
    assert "focused no-regrowth guard home for Phase 96 sanitizer burn-down" in file_matrix_text
    assert "focused closeout guard home for Phase 97 governance / assurance freeze" in file_matrix_text

    assert "`390` Python files under `tests`" in testing_text
    assert "`310` runnable `test_*.py` files" in testing_text
    assert "`55` meta suites" in testing_text
    assert "tests/meta/test_phase96_sanitizer_burndown_guards.py" in verification_text
    assert "tests/meta/test_phase97_governance_assurance_freeze_guards.py" in verification_text
    assert "## Phase 97 Governance / Open-Source Contract Sync and Assurance Freeze" in verification_text
