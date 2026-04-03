"""Focused predecessor guards for Phase 103 root thinning and terminology normalization."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import (
    assert_current_route_markers,
    assert_testing_inventory_snapshot,
)
from .governance_current_truth import CURRENT_MILESTONE_STATUS

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
_DEV_ARCH = _ROOT / "docs" / "architecture_archive.md"
_ADR = _ROOT / "docs" / "adr" / "0005-entry-surface-terminology-contract.md"
_PHASE_DIR = (
    _ROOT
    / ".planning"
    / "phases"
    / "103-root-adapter-thinning-test-topology-second-pass-and-terminology-contract-normalization"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase103_predecessor_bundle_remains_visible_under_phase105_route() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    verification_text = _read(_VERIFICATION_MATRIX)
    dev_arch_text = _read(_DEV_ARCH)
    adr_text = _read(_ADR)
    verification_doc = _read(_PHASE_DIR / "103-VERIFICATION.md")
    validation_doc = _read(_PHASE_DIR / "103-VALIDATION.md")

    assert_current_route_markers(
        project_text,
        roadmap_text,
        requirements_text,
        state_text,
        milestones_text,
        verification_text,
    )

    assert CURRENT_MILESTONE_STATUS in project_text
    assert CURRENT_MILESTONE_STATUS in roadmap_text
    assert (
        "Phase 103 Root Adapter Thinning / Test Topology Second Pass / Terminology Contract Note"
        in dev_arch_text
    )
    assert "ADR-0005" in adr_text
    assert "# Phase 103 Verification" in verification_doc
    assert "# Phase 103 Validation Contract" in validation_doc


def test_phase103_maps_and_ledgers_project_new_helper_homes() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    residual_text = _read(_RESIDUAL)
    kill_text = _read(_KILL)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)

    assert "custom_components/lipro/control/entry_root_support.py" in file_matrix_text
    assert "tests/topicized_collection.py" in file_matrix_text
    assert "tests/coordinator_double.py" in file_matrix_text
    assert "tests/meta/test_phase103_root_thinning_guards.py" in file_matrix_text
    assert (
        "focused predecessor guard home for Phase 103 root thinning / test topology / terminology normalization"
        in file_matrix_text
    )
    assert "## Phase 103 Residual Delta" in residual_text
    assert "## Phase 103 Status Update" in kill_text
    assert "## Phase 103 Testing Freeze" in testing_text
    assert_testing_inventory_snapshot(testing_text)
    assert (
        "## Phase 103 Root Adapter Thinning / Test Topology Second Pass / Terminology Contract Normalization"
        in verification_text
    )


def test_phase103_root_wiring_stays_explicit_and_patch_friendly() -> None:
    support_text = _read(
        _ROOT / "custom_components" / "lipro" / "control" / "entry_root_support.py"
    )
    wiring_text = _read(
        _ROOT / "custom_components" / "lipro" / "control" / "entry_root_wiring.py"
    )
    root_text = _read(_ROOT / "custom_components" / "lipro" / "__init__.py")

    assert "def load_module(" not in support_text
    assert "def load_entry_lifecycle_controller_factory(" in support_text
    assert "controller_module_name" not in wiring_text
    assert "load_module:" not in wiring_text
    assert "controller_factory=_load_entry_lifecycle_controller_factory()" in root_text
    assert "load_module as _load_module" not in root_text
