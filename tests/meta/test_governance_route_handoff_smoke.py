"""Focused route-handoff smoke guards for active-route handoff and latest-archive truth."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

import pytest

from tests.helpers.repo_root import repo_root

from .conftest import _as_bool, _as_mapping, _as_mapping_list, _as_str
from .governance_contract_helpers import (
    _assert_current_route_truth,
    assert_current_route_focused_guards,
)
from .governance_current_truth import (
    CURRENT_MILESTONE,
    CURRENT_MILESTONE_COMPLETED_PHASES,
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_PENDING_PHASES,
    CURRENT_MILESTONE_PHASES,
    CURRENT_MILESTONE_PLAN_COUNT,
    CURRENT_MILESTONE_PLAN_COUNT_BY_PHASE,
    CURRENT_MILESTONE_STATUS,
    CURRENT_MILESTONE_SUMMARY_COUNT_BY_PHASE,
    CURRENT_PHASE,
    CURRENT_ROUTE,
    LATEST_ARCHIVED_EVIDENCE_PATH,
)
from .governance_promoted_assets import _assert_promoted_phase_assets

_ROOT = repo_root(Path(__file__))
_GSD_TOOLS = Path.home() / ".codex" / "get-shit-done" / "bin" / "gsd-tools.cjs"


def _run_gsd_tools(*args: str) -> dict[str, object]:
    node_executable = shutil.which("node")
    if node_executable is None:
        pytest.skip("node unavailable; skipping gsd fast-path smoke")
    if not _GSD_TOOLS.exists():
        pytest.skip("gsd-tools unavailable; skipping gsd fast-path smoke")
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
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    verification_text = (_ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md").read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(encoding="utf-8")

    _assert_current_route_truth(project_text, roadmap_text, state_text)

    assert CURRENT_ROUTE in project_text
    assert CURRENT_MILESTONE_STATUS in project_text
    assert CURRENT_MILESTONE_STATUS in roadmap_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in project_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in roadmap_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in state_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in requirements_text
    assert "## Phase 103 Root Adapter Thinning / Test Topology Second Pass / Terminology Contract Normalization" in verification_text
    assert "## Phase 104 Service-router Family Split / Command-runtime Second-pass Decomposition" in verification_text
    assert "## Phase 105 Governance Rule Datafication / Milestone Freeze" in verification_text
    assert "## Phase 107 REST/Auth/Status Hotspot Convergence / Support-surface Slimming" in verification_text
    assert "## Phase 108 MQTT Transport-runtime De-friendization" in verification_text
    assert "## Phase 109 Anonymous-share Manager Inward Decomposition" in verification_text
    assert "## Phase 111 Entity / Runtime Boundary Sealing and Dependency-Guard Hardening" in verification_text
    assert "## Phase 101 Anonymous-share Manager / REST Decoder Hotspot Decomposition Freeze" in verification_text
    assert CURRENT_ROUTE in verification_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in verification_text
    assert LATEST_ARCHIVED_EVIDENCE_PATH in verification_text
    assert_current_route_focused_guards(verification_text)
    for guard in (
        "tests/meta/test_governance_route_handoff_smoke.py",
        "tests/meta/test_phase98_route_reactivation_guards.py",
        "tests/meta/test_phase99_runtime_hotspot_support_guards.py",
        "tests/meta/test_phase100_runtime_schedule_support_guards.py",
        "tests/meta/test_phase101_anonymous_share_rest_boundary_guards.py",
        "tests/meta/test_phase102_governance_portability_guards.py",
        "tests/meta/test_phase103_root_thinning_guards.py",
        "tests/meta/test_phase104_service_router_runtime_split_guards.py",
        "tests/meta/test_phase105_governance_freeze_guards.py",
        "tests/meta/test_phase107_rest_status_hotspot_guards.py",
        "tests/meta/test_phase108_mqtt_transport_de_friendization_guards.py",
        "tests/meta/test_phase109_anonymous_share_manager_inward_decomposition_guards.py",
        "tests/meta/test_phase110_runtime_snapshot_closeout_guards.py",
        "tests/meta/test_phase111_runtime_boundary_guards.py",
    ):
        assert guard in file_matrix_text
    assert "route-handoff gsd fast-path smoke guard home" in file_matrix_text


def test_gsd_fast_path_matches_current_active_route_story() -> None:
    progress = _run_gsd_tools("init", "progress")
    phases = _as_mapping_list(progress["phases"])

    assert [_as_str(phase["number"]) for phase in phases] == list(CURRENT_MILESTONE_PHASES)
    phase_by_number = {_as_str(phase["number"]): phase for phase in phases}

    for phase_number in CURRENT_MILESTONE_COMPLETED_PHASES:
        phase_progress = _as_mapping(phase_by_number[phase_number])
        assert _as_str(phase_progress["status"]) == "complete"
        assert phase_progress["plan_count"] == CURRENT_MILESTONE_PLAN_COUNT_BY_PHASE[phase_number]
        assert phase_progress["summary_count"] == CURRENT_MILESTONE_SUMMARY_COUNT_BY_PHASE[phase_number]

    for phase_number in CURRENT_MILESTONE_PENDING_PHASES:
        phase_progress = _as_mapping(phase_by_number[phase_number])
        assert _as_str(phase_progress["status"]) == "not_started"
        assert phase_progress["plan_count"] == CURRENT_MILESTONE_PLAN_COUNT_BY_PHASE[phase_number]
        assert phase_progress["summary_count"] == CURRENT_MILESTONE_SUMMARY_COUNT_BY_PHASE[phase_number]

    assert progress["current_phase"] is None
    assert _as_bool(progress["has_work_in_progress"]) is False

    assert progress["next_phase"] is None

    completed_phase = CURRENT_MILESTONE_COMPLETED_PHASES[-1]
    phase_index = _run_gsd_tools("phase-plan-index", completed_phase)
    assert _as_str(phase_index["phase"]) == completed_phase
    assert len(_as_mapping_list(phase_index["plans"])) == CURRENT_MILESTONE_PLAN_COUNT_BY_PHASE[completed_phase]

    state = _run_gsd_tools("state", "json")
    assert _as_str(state["milestone"]) == CURRENT_MILESTONE
    assert _as_str(state["status"]) == CURRENT_MILESTONE_STATUS
    assert _as_mapping(state["progress"]) == {
        "total_phases": str(len(CURRENT_MILESTONE_PHASES)),
        "completed_phases": str(len(CURRENT_MILESTONE_COMPLETED_PHASES)),
        "total_plans": "13",
        "completed_plans": "13",
        "percent": "100",
    }

    plan_init = _run_gsd_tools("init", "plan-phase", CURRENT_PHASE)
    assert _as_bool(plan_init["phase_found"]) is True
    assert _as_str(plan_init["phase_number"]) == CURRENT_PHASE
    assert _as_bool(plan_init["has_plans"]) is True
    assert _as_bool(plan_init["has_context"]) is True
    assert _as_bool(plan_init["has_research"]) is True
    assert plan_init["plan_count"] == CURRENT_MILESTONE_PLAN_COUNT

    execute_init = _run_gsd_tools("init", "execute-phase", CURRENT_PHASE)
    assert _as_bool(execute_init["phase_found"]) is True
    assert _as_str(execute_init["phase_number"]) == CURRENT_PHASE
    assert execute_init["plan_count"] == CURRENT_MILESTONE_PLAN_COUNT
    plans = execute_init["plans"]
    assert isinstance(plans, list)
    assert len(plans) == CURRENT_MILESTONE_PLAN_COUNT


def test_recent_governance_closeout_assets_are_promoted_without_planning_traces() -> None:
    for slug, assets in (
        (
            "76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation",
            ("76-01-SUMMARY.md", "76-02-SUMMARY.md", "76-03-SUMMARY.md", "76-VERIFICATION.md", "76-VALIDATION.md"),
        ),
        (
            "77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction",
            ("77-01-SUMMARY.md", "77-02-SUMMARY.md", "77-03-SUMMARY.md", "77-VERIFICATION.md", "77-VALIDATION.md"),
        ),
        (
            "78-quality-gate-formalization-route-handoff-ergonomics-and-milestone-closeout-readiness",
            ("78-01-SUMMARY.md", "78-02-SUMMARY.md", "78-03-SUMMARY.md", "78-SUMMARY.md", "78-VERIFICATION.md", "78-VALIDATION.md"),
        ),
        (
            "79-governance-tooling-hotspot-decomposition-and-release-contract-topicization",
            ("79-01-SUMMARY.md", "79-02-SUMMARY.md", "79-03-SUMMARY.md", "79-SUMMARY.md", "79-VERIFICATION.md", "79-VALIDATION.md"),
        ),
        (
            "80-governance-typing-closure-and-final-meta-suite-hotspot-topicization",
            ("80-01-SUMMARY.md", "80-02-SUMMARY.md", "80-03-SUMMARY.md", "80-SUMMARY.md", "80-VERIFICATION.md", "80-VALIDATION.md"),
        ),
        (
            "81-contributor-onramp-route-convergence-and-public-entry-contract",
            ("81-01-SUMMARY.md", "81-02-SUMMARY.md", "81-03-SUMMARY.md", "81-SUMMARY.md", "81-VERIFICATION.md", "81-VALIDATION.md"),
        ),
        (
            "82-release-operations-closure-and-evidence-chain-formalization",
            ("82-01-SUMMARY.md", "82-02-SUMMARY.md", "82-03-SUMMARY.md", "82-SUMMARY.md", "82-VERIFICATION.md", "82-VALIDATION.md"),
        ),
        (
            "83-intake-templates-and-maintainer-stewardship-contract",
            ("83-01-SUMMARY.md", "83-02-SUMMARY.md", "83-03-SUMMARY.md", "83-SUMMARY.md", "83-VERIFICATION.md", "83-VALIDATION.md"),
        ),
        (
            "84-governance-open-source-guard-coverage-and-milestone-truth-freeze",
            ("84-01-SUMMARY.md", "84-02-SUMMARY.md", "84-03-SUMMARY.md", "84-SUMMARY.md", "84-VERIFICATION.md", "84-VALIDATION.md"),
        ),
        (
            "88-governance-sync-quality-proof-and-milestone-freeze",
            ("88-01-SUMMARY.md", "88-02-SUMMARY.md", "88-03-SUMMARY.md", "88-SUMMARY.md", "88-VERIFICATION.md", "88-VALIDATION.md"),
        ),
        (
            "102-governance-portability-verification-stratification-and-open-source-continuity-hardening",
            ("102-01-SUMMARY.md", "102-02-SUMMARY.md", "102-03-SUMMARY.md", "102-VERIFICATION.md", "102-VALIDATION.md"),
        ),
        (
            "105-governance-rule-datafication-and-milestone-freeze",
            ("105-01-SUMMARY.md", "105-02-SUMMARY.md", "105-03-SUMMARY.md", "105-SUMMARY.md", "105-VERIFICATION.md", "105-VALIDATION.md"),
        ),
    ):
        _assert_promoted_phase_assets(slug, *assets)
