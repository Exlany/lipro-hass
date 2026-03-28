"""Focused closeout guards for Phase 98 route reactivation and carry-forward closure."""

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
_PUBLIC_SURFACES = _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_RESIDUAL_LEDGER = _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
_TESTING = _ROOT / ".planning" / "codebase" / "TESTING.md"
_CONCERNS = _ROOT / ".planning" / "codebase" / "CONCERNS.md"
_DEV_ARCH = _ROOT / "docs" / "developer_architecture.md"
_DEVICE = _ROOT / "custom_components" / "lipro" / "core" / "device" / "device.py"
_PHASE98_DIR = (
    _ROOT
    / ".planning"
    / "phases"
    / "98-carry-forward-eradication-route-reactivation-and-closeout-proof"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase98_current_route_docs_and_closeout_bundle_align() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    verification_text = _read(_VERIFICATION_MATRIX)
    dev_arch_text = _read(_DEV_ARCH)
    phase98_verification = _read(_PHASE98_DIR / "98-VERIFICATION.md")
    phase98_validation = _read(_PHASE98_DIR / "98-VALIDATION.md")

    for text in (
        project_text,
        roadmap_text,
        requirements_text,
        state_text,
        milestones_text,
        verification_text,
    ):
        assert (
            "v1.27 active route / Phase 98 complete / latest archived baseline = v1.26"
            in text
        )
        assert "$gsd-complete-milestone v1.27" in text

    assert "active / closeout-ready (2026-03-28)" in project_text
    assert "active / closeout-ready (2026-03-28)" in roadmap_text
    assert "active / closeout-ready (2026-03-28)" in requirements_text
    assert "active / closeout-ready (2026-03-28)" in state_text
    assert "active / closeout-ready (2026-03-28)" in milestones_text
    assert "Phase 98 Route Reactivation / Carry-Forward Closure Note" in dev_arch_text
    assert "# Phase 98 Verification" in phase98_verification
    assert "# Phase 98 Validation Contract" in phase98_validation


def test_phase98_file_and_testing_maps_freeze_new_guard_footprint() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)

    assert "tests/meta/test_phase98_route_reactivation_guards.py" in file_matrix_text
    assert (
        "focused current-route guard home for Phase 98 reactivation / carry-forward closure"
        in file_matrix_text
    )
    assert "`391` Python files under `tests`" in testing_text
    assert "`311` runnable `test_*.py` files" in testing_text
    assert "`56` meta suites" in testing_text
    assert "tests/meta/test_phase98_route_reactivation_guards.py" in verification_text
    assert (
        "## Phase 98 Carry-Forward Eradication / Route Reactivation / Closeout Proof"
        in verification_text
    )


def test_phase98_outlet_power_formal_primitive_has_no_live_legacy_fallback_story() -> (
    None
):
    device_text = _read(_DEVICE)
    public_surfaces_text = _read(_PUBLIC_SURFACES)
    concerns_text = _read(_CONCERNS)
    residual_text = _read(_RESIDUAL_LEDGER)

    assert 'extra_data.get("power_info")' not in device_text
    assert "legacy_power_info" not in device_text
    assert 'self.extra_data.pop("power_info", None)' in device_text
    assert "legacy read fallback" not in public_surfaces_text
    assert "Legacy outlet-power side-car fallback remains:" not in concerns_text
    assert "legacy_power_info" not in concerns_text
    assert "Phase 98 已关闭该 carry-forward" in residual_text
