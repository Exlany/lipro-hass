"""Phase-agnostic changed-surface assurance route guards."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_LINT = _ROOT / "scripts" / "lint"


def test_changed_surface_assurance_routes_use_phase_agnostic_guard_home() -> None:
    lint_text = _LINT.read_text(encoding="utf-8")

    for token in (
        "tests/core/test_share_client_submit.py tests/meta/test_changed_surface_assurance_guards.py",
        "tests/core/test_command_result.py tests/meta/test_changed_surface_assurance_guards.py",
        "uv run pytest -q tests/meta/test_changed_surface_assurance_guards.py",
        "tests/meta/toolchain_truth_ci_contract.py tests/meta/test_governance_release_docs.py tests/meta/toolchain_truth_docs_fast_path.py",
        "tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py",
        "Running scripts/lint in default mode with focused changed-surface assurance when matching touched surfaces are detected...",
    ):
        assert token in lint_text

    assert "tests/meta/test_phase113_hotspot_assurance_guards.py" not in lint_text
    assert "hotspot_assurance_guards" not in lint_text
