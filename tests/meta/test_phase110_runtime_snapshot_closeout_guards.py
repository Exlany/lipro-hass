"""Focused active-route guards for Phase 110 runtime snapshot closeout."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_STATUS,
    CURRENT_ROUTE,
)

_ROOT = repo_root(Path(__file__))
_PROJECT = _ROOT / ".planning" / "PROJECT.md"
_ROADMAP = _ROOT / ".planning" / "ROADMAP.md"
_REQUIREMENTS = _ROOT / ".planning" / "REQUIREMENTS.md"
_STATE = _ROOT / ".planning" / "STATE.md"
_MILESTONES = _ROOT / ".planning" / "MILESTONES.md"
_VERIFICATION_MATRIX = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_RESIDUAL = _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
_KILL = _ROOT / ".planning" / "reviews" / "KILL_LIST.md"
_TESTING = _ROOT / ".planning" / "codebase" / "TESTING.md"
_DEV_ARCH = _ROOT / "docs" / "developer_architecture.md"
_SNAPSHOT = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "runtime" / "device" / "snapshot.py"
_SNAPSHOT_SUPPORT = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "runtime" / "device" / "snapshot_support.py"
_SNAPSHOT_SUPPORT_TEST = _ROOT / "tests" / "core" / "coordinator" / "runtime" / "test_snapshot_support.py"
_PHASE_DIR = _ROOT / ".planning" / "phases" / "110-runtime-snapshot-surface-reduction-and-milestone-closeout"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase110_active_route_bundle_is_current_truth() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    verification_text = _read(_VERIFICATION_MATRIX)
    dev_arch_text = _read(_DEV_ARCH)
    verification_doc = _read(_PHASE_DIR / "110-VERIFICATION.md")
    validation_doc = _read(_PHASE_DIR / "110-VALIDATION.md")

    for text in (
        project_text,
        roadmap_text,
        requirements_text,
        state_text,
        milestones_text,
        verification_text,
    ):
        assert CURRENT_ROUTE in text
        assert CURRENT_MILESTONE_DEFAULT_NEXT in text

    assert CURRENT_MILESTONE_STATUS in project_text
    assert CURRENT_MILESTONE_STATUS in roadmap_text
    assert "### Phase 110: Runtime snapshot surface reduction and milestone closeout" in roadmap_text
    assert "## Current Milestone (v1.30)" in project_text
    assert "## Current Milestone (v1.30)" in requirements_text
    assert "## Current Milestone (v1.30)" in milestones_text
    assert "Phase 110 Runtime Snapshot Surface Reduction and Milestone Closeout Note" in dev_arch_text
    assert "# Phase 110 Verification" in verification_doc
    assert "# Phase 110 Validation Contract" in validation_doc


def test_phase110_ledgers_testing_and_file_matrix_freeze_the_same_story() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    residual_text = _read(_RESIDUAL)
    kill_text = _read(_KILL)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)

    for path in (
        "custom_components/lipro/core/coordinator/runtime/device/snapshot.py",
        "custom_components/lipro/core/coordinator/runtime/device/snapshot_support.py",
        "tests/core/coordinator/runtime/test_snapshot_support.py",
        "tests/meta/test_phase110_runtime_snapshot_closeout_guards.py",
    ):
        assert path in file_matrix_text
    assert (
        "focused active-route guard home for Phase 110 runtime snapshot surface reduction and milestone closeout"
        in file_matrix_text
    )
    assert "## Phase 110 Residual Delta" in residual_text
    assert "## Phase 110 Status Update" in kill_text
    assert "## Phase 110 Testing Freeze" in testing_text
    assert_testing_inventory_snapshot(testing_text)
    assert (
        "## Phase 110 Runtime Snapshot Surface Reduction / Milestone Closeout"
        in verification_text
    )
    for token in (
        "$gsd-complete-milestone v1.30",
        "tests/meta/test_phase110_runtime_snapshot_closeout_guards.py",
        ".planning/phases/110-runtime-snapshot-surface-reduction-and-milestone-closeout/{110-01-SUMMARY.md,110-02-SUMMARY.md,110-03-SUMMARY.md,110-04-SUMMARY.md,110-05-SUMMARY.md,110-06-SUMMARY.md,110-SUMMARY.md,110-VERIFICATION.md,110-VALIDATION.md}",
        ".planning/reviews/V1_30_EVIDENCE_INDEX.md",
        ".planning/v1.30-MILESTONE-AUDIT.md",
    ):
        assert token in verification_text


def test_phase110_code_boundaries_keep_single_snapshot_outward_home() -> None:
    snapshot_text = _read(_SNAPSHOT)
    support_text = _read(_SNAPSHOT_SUPPORT)
    support_test_text = _read(_SNAPSHOT_SUPPORT_TEST)

    for token in (
        "class SnapshotBuilder:",
        "record_snapshot_device(",
        "canonicalize_device_row(device_data)",
        "device_ref_from_row(device_data)",
        "canonical_page_has_more(",
    ):
        assert token in snapshot_text

    for token in (
        "class SnapshotAssembly:",
        "def coerce_total_count(",
        "def canonicalize_device_row(",
        "def build_index_identity_aliases(",
        "def record_snapshot_device(",
    ):
        assert token in support_text

    for token in (
        "def test_coerce_total_count_handles_supported_inputs(",
        "def test_record_snapshot_device_populates_indexes_and_categories(",
        "def test_record_snapshot_device_splits_group_outlet_and_gateway(",
    ):
        assert token in support_test_text
