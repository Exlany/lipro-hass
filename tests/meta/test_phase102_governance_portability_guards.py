"""Focused latest-archived guards for Phase 102 governance portability and closeout hardening."""

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
_AUDIT = _ROOT / ".planning" / "v1.28-MILESTONE-AUDIT.md"
_EVIDENCE = _ROOT / ".planning" / "reviews" / "V1_28_EVIDENCE_INDEX.md"
_VERIFICATION_MATRIX = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_TESTING = _ROOT / ".planning" / "codebase" / "TESTING.md"
_PROMOTED = _ROOT / ".planning" / "reviews" / "PROMOTED_PHASE_ASSETS.md"
_RESIDUAL = _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
_KILL = _ROOT / ".planning" / "reviews" / "KILL_LIST.md"
_DEV_ARCH = _ROOT / "docs" / "developer_architecture.md"
_RUNBOOK = _ROOT / "docs" / "MAINTAINER_RELEASE_RUNBOOK.md"
_PHASE102_DIR = (
    _ROOT
    / ".planning"
    / "phases"
    / "102-governance-portability-verification-stratification-and-open-source-continuity-hardening"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase102_latest_archived_closeout_bundle_is_the_current_truth() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    audit_text = _read(_AUDIT)
    evidence_text = _read(_EVIDENCE)
    verification_text = _read(_VERIFICATION_MATRIX)
    dev_arch_text = _read(_DEV_ARCH)
    runbook_text = _read(_RUNBOOK)
    summary_text = _read(_PHASE102_DIR / "102-03-SUMMARY.md")
    verification_doc = _read(_PHASE102_DIR / "102-VERIFICATION.md")
    validation_doc = _read(_PHASE102_DIR / "102-VALIDATION.md")

    for text in (
        project_text,
        roadmap_text,
        requirements_text,
        state_text,
        milestones_text,
        verification_text,
        evidence_text,
    ):
        assert "no active milestone route / latest archived baseline = v1.28" in text
        assert "$gsd-new-milestone" in text

    assert "Phase 102" in project_text
    assert "Phase 102" in roadmap_text
    assert "Phase 102" in requirements_text
    assert "Phase 102" in state_text
    assert "Phase 102" in milestones_text
    assert "Phase 102 Governance Portability / Verification Stratification / Open-Source Continuity Hardening Note" in dev_arch_text
    assert "V1_28_EVIDENCE_INDEX.md" in runbook_text
    assert "v1.28-MILESTONE-AUDIT.md" in runbook_text
    assert "no active milestone route / latest archived baseline = v1.28" in audit_text
    assert "# v1.28 Evidence Index" in evidence_text
    assert "# Phase 102 Verification" in verification_doc
    assert "# Phase 102 Validation Contract" in validation_doc
    assert "Phase 102" in summary_text


def test_phase102_maps_and_ledgers_freeze_portability_hardening() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    testing_text = _read(_TESTING)
    promoted_text = _read(_PROMOTED)
    residual_text = _read(_RESIDUAL)
    kill_text = _read(_KILL)
    verification_text = _read(_VERIFICATION_MATRIX)

    assert "tests/meta/test_phase102_governance_portability_guards.py" in file_matrix_text
    assert "focused latest-archived guard home for Phase 102 governance portability / verification stratification / open-source continuity hardening" in file_matrix_text
    assert_testing_inventory_snapshot(testing_text)
    assert "Phase 102" in testing_text
    assert "102-governance-portability-verification-stratification-and-open-source-continuity-hardening" in promoted_text
    assert "102-VERIFICATION.md" in promoted_text
    assert "## Phase 102 Residual Delta" in residual_text
    assert "## Phase 102 Status Update" in kill_text
    assert "## Phase 102 Governance Portability / Verification Stratification / Open-Source Continuity Hardening" in verification_text
