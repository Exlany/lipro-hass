"""Focused predecessor guards for Phase 98 route reactivation and carry-forward closure."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot
from .governance_current_truth import CURRENT_PHASE, CURRENT_ROUTE

_ROOT = repo_root(Path(__file__))
_PROJECT = _ROOT / ".planning" / "PROJECT.md"
_ROADMAP = _ROOT / ".planning" / "ROADMAP.md"
_ARCHIVED_V127_REQUIREMENTS = _ROOT / ".planning" / "milestones" / "v1.27-REQUIREMENTS.md"
_STATE = _ROOT / ".planning" / "STATE.md"
_MILESTONES = _ROOT / ".planning" / "MILESTONES.md"
_VERIFICATION_MATRIX = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
_PUBLIC_SURFACES = _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_RESIDUAL_LEDGER = _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
_TESTING = _ROOT / ".planning" / "codebase" / "TESTING.md"
_DEV_ARCH = _ROOT / "docs" / "architecture_archive.md"
_DEVICE = _ROOT / "custom_components" / "lipro" / "core" / "device" / "device.py"
_PHASE98_DIR = (
    _ROOT
    / ".planning"
    / "phases"
    / "98-carry-forward-eradication-route-reactivation-and-closeout-proof"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase98_bundle_stays_visible_as_completed_predecessor() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_ARCHIVED_V127_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    dev_arch_text = _read(_DEV_ARCH)
    phase98_verification = _read(_PHASE98_DIR / "98-VERIFICATION.md")
    phase98_validation = _read(_PHASE98_DIR / "98-VALIDATION.md")

    assert CURRENT_ROUTE in project_text
    assert (
        "### Phase 98: Carry-forward eradication, route reactivation, and closeout proof"
        in roadmap_text
    )
    assert "| RES-15 | Phase 98 | Completed |" in requirements_text
    assert f"Phase {CURRENT_PHASE}" in state_text
    assert "`Phase 98`: carry-forward eradication, route reactivation, and closeout proof ✅" in milestones_text
    assert "Phase 98 Route Reactivation / Carry-Forward Closure Note" in dev_arch_text
    assert "# Phase 98 Verification" in phase98_verification
    assert "# Phase 98 Validation Contract" in phase98_validation


def test_phase98_maps_keep_predecessor_guard_footprint() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)

    assert "tests/meta/test_phase98_route_reactivation_guards.py" in file_matrix_text
    assert "focused predecessor guard home for Phase 98 reactivation / carry-forward closure" in file_matrix_text
    assert_testing_inventory_snapshot(testing_text)
    assert "tests/meta/test_phase98_route_reactivation_guards.py" in verification_text
    assert "## Phase 98 Carry-Forward Eradication / Route Reactivation / Closeout Proof" in verification_text
    assert "## Phase 102 Governance Portability / Verification Stratification / Open-Source Continuity Hardening" in verification_text


def test_phase98_outlet_power_formal_primitive_has_no_live_legacy_fallback_story() -> None:
    device_text = _read(_DEVICE)
    public_surfaces_text = _read(_PUBLIC_SURFACES)
    residual_text = _read(_RESIDUAL_LEDGER)

    assert 'extra_data.get("power_info")' not in device_text
    assert "legacy_power_info" not in device_text
    assert 'self.extra_data.pop("power_info", None)' in device_text
    assert "legacy read fallback" not in public_surfaces_text
    assert "Phase 98 已关闭该 carry-forward" in residual_text
