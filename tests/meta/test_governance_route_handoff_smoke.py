"""Focused route-handoff smoke guards for the active-route handoff and latest-archive truth."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

from tests.helpers.repo_root import repo_root

from .conftest import _as_bool, _as_mapping, _as_mapping_list, _as_str
from .governance_contract_helpers import _assert_current_route_truth
from .governance_current_truth import (
    CURRENT_MILESTONE,
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_STATUS,
    CURRENT_ROUTE,
    LATEST_ARCHIVED_EVIDENCE_PATH,
)
from .governance_promoted_assets import _assert_promoted_phase_assets

_ROOT = repo_root(Path(__file__))
_GSD_TOOLS = Path.home() / ".codex" / "get-shit-done" / "bin" / "gsd-tools.cjs"


def _run_gsd_tools(*args: str) -> dict[str, object]:
    node_executable = shutil.which("node")
    assert node_executable is not None
    result = subprocess.run(  # noqa: S603
        [node_executable, str(_GSD_TOOLS), *args],
        cwd=_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = result.stdout.strip()
    if payload.startswith("@file:"):
        payload = Path(payload.removeprefix("@file:")).read_text(encoding="utf-8")
    loaded = json.loads(payload)
    assert isinstance(loaded, dict)
    return loaded


def test_route_handoff_docs_and_ledgers_stay_in_sync() -> None:
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )

    _assert_current_route_truth(project_text, roadmap_text, state_text)

    assert CURRENT_ROUTE in project_text
    assert CURRENT_MILESTONE_STATUS in project_text
    assert CURRENT_MILESTONE_STATUS in roadmap_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in project_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in roadmap_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in state_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in requirements_text
    assert (
        "## Phase 98 Carry-Forward Eradication / Route Reactivation / Closeout Proof"
        in verification_text
    )
    assert (
        "## Phase 99 Runtime Hotspot Support Extraction / Terminal Audit Freeze"
        in verification_text
    )
    assert CURRENT_ROUTE in verification_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in verification_text
    assert LATEST_ARCHIVED_EVIDENCE_PATH in verification_text
    assert "tests/meta/test_governance_route_handoff_smoke.py" in verification_text
    assert "tests/meta/test_phase94_typed_boundary_guards.py" in verification_text
    assert (
        "tests/meta/test_phase95_hotspot_decomposition_guards.py" in verification_text
    )
    assert "tests/meta/test_phase96_sanitizer_burndown_guards.py" in verification_text
    assert (
        "tests/meta/test_phase97_governance_assurance_freeze_guards.py"
        in verification_text
    )
    assert "tests/meta/test_phase98_route_reactivation_guards.py" in verification_text
    assert "tests/meta/test_phase99_runtime_hotspot_support_guards.py" in verification_text
    assert "tests/meta/test_governance_route_handoff_smoke.py" in file_matrix_text
    assert "tests/meta/test_phase94_typed_boundary_guards.py" in file_matrix_text
    assert "tests/meta/test_phase95_hotspot_decomposition_guards.py" in file_matrix_text
    assert "tests/meta/test_phase96_sanitizer_burndown_guards.py" in file_matrix_text
    assert (
        "tests/meta/test_phase97_governance_assurance_freeze_guards.py"
        in file_matrix_text
    )
    assert "tests/meta/test_phase98_route_reactivation_guards.py" in file_matrix_text
    assert "tests/meta/test_phase99_runtime_hotspot_support_guards.py" in file_matrix_text
    assert "route-handoff gsd fast-path smoke guard home" in file_matrix_text


def test_gsd_fast_path_matches_current_active_route_story() -> None:
    progress = _run_gsd_tools("init", "progress")
    phases = _as_mapping_list(progress["phases"])

    assert [_as_str(phase["number"]) for phase in phases] == ["98", "99"]
    phase_98, phase_99 = phases

    assert _as_str(phase_98["status"]) == "complete"
    assert phase_98["plan_count"] == 3
    assert phase_98["summary_count"] == 3
    assert phase_99["plan_count"] == 3
    current_phase = progress.get("current_phase")
    assert current_phase is None or _as_str(current_phase) == "99"

    phase_index = _run_gsd_tools("phase-plan-index", "99")
    assert _as_str(phase_index["phase"]) == "99"
    assert len(_as_mapping_list(phase_index["plans"])) == 3

    state = _run_gsd_tools("state", "json")
    assert _as_str(state["milestone"]) == CURRENT_MILESTONE
    assert _as_str(state["status"]) == "active"
    assert _as_mapping(state["progress"]) == {
        "total_phases": "2",
        "completed_phases": "2",
        "total_plans": "6",
        "completed_plans": "6",
    }

    plan_init = _run_gsd_tools("init", "plan-phase", "99")
    assert _as_bool(plan_init["phase_found"]) is True
    assert _as_str(plan_init["phase_number"]) == "99"
    assert _as_bool(plan_init["has_plans"]) is True
    assert _as_bool(plan_init["has_context"]) is True
    assert _as_bool(plan_init["has_research"]) is True
    assert plan_init["plan_count"] == 3

    execute_init = _run_gsd_tools("init", "execute-phase", "99")
    assert _as_bool(execute_init["phase_found"]) is True
    assert _as_str(execute_init["phase_number"]) == "99"
    assert execute_init["plan_count"] == 3
    plans = execute_init["plans"]
    assert isinstance(plans, list)
    assert len(plans) == 3


def test_recent_governance_closeout_assets_are_promoted_without_planning_traces() -> (
    None
):
    _assert_promoted_phase_assets(
        "76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation",
        "76-01-SUMMARY.md",
        "76-02-SUMMARY.md",
        "76-03-SUMMARY.md",
        "76-VERIFICATION.md",
        "76-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction",
        "77-01-SUMMARY.md",
        "77-02-SUMMARY.md",
        "77-03-SUMMARY.md",
        "77-VERIFICATION.md",
        "77-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "78-quality-gate-formalization-route-handoff-ergonomics-and-milestone-closeout-readiness",
        "78-01-SUMMARY.md",
        "78-02-SUMMARY.md",
        "78-03-SUMMARY.md",
        "78-SUMMARY.md",
        "78-VERIFICATION.md",
        "78-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "79-governance-tooling-hotspot-decomposition-and-release-contract-topicization",
        "79-01-SUMMARY.md",
        "79-02-SUMMARY.md",
        "79-03-SUMMARY.md",
        "79-SUMMARY.md",
        "79-VERIFICATION.md",
        "79-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "80-governance-typing-closure-and-final-meta-suite-hotspot-topicization",
        "80-01-SUMMARY.md",
        "80-02-SUMMARY.md",
        "80-03-SUMMARY.md",
        "80-SUMMARY.md",
        "80-VERIFICATION.md",
        "80-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "81-contributor-onramp-route-convergence-and-public-entry-contract",
        "81-01-SUMMARY.md",
        "81-02-SUMMARY.md",
        "81-03-SUMMARY.md",
        "81-SUMMARY.md",
        "81-VERIFICATION.md",
        "81-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "82-release-operations-closure-and-evidence-chain-formalization",
        "82-01-SUMMARY.md",
        "82-02-SUMMARY.md",
        "82-03-SUMMARY.md",
        "82-SUMMARY.md",
        "82-VERIFICATION.md",
        "82-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "83-intake-templates-and-maintainer-stewardship-contract",
        "83-01-SUMMARY.md",
        "83-02-SUMMARY.md",
        "83-03-SUMMARY.md",
        "83-SUMMARY.md",
        "83-VERIFICATION.md",
        "83-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "84-governance-open-source-guard-coverage-and-milestone-truth-freeze",
        "84-01-SUMMARY.md",
        "84-02-SUMMARY.md",
        "84-03-SUMMARY.md",
        "84-SUMMARY.md",
        "84-VERIFICATION.md",
        "84-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "88-governance-sync-quality-proof-and-milestone-freeze",
        "88-01-SUMMARY.md",
        "88-02-SUMMARY.md",
        "88-03-SUMMARY.md",
        "88-SUMMARY.md",
        "88-VERIFICATION.md",
        "88-VALIDATION.md",
    )
