"""Phase 71 hotspot/function-budget and active-route truth guards."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import _assert_latest_archived_route_truth
from .governance_current_truth import (
    LATEST_ARCHIVED_PHASE_TITLE,
    PREVIOUS_ARCHIVED_MILESTONE,
)

_ROOT = repo_root(Path(__file__))
_FUNCTION_BUDGETS = {
    ("custom_components/lipro/entities/firmware_update.py", "async_install"): 20,
    ("custom_components/lipro/core/api/diagnostics_api_ota.py", "_query_primary_ota_rows"): 70,
    ("custom_components/lipro/core/api/diagnostics_api_ota.py", "query_ota_info_with_outcome"): 50,
    ("custom_components/lipro/core/anonymous_share/share_client_submit.py", "submit_share_payload_with_outcome"): 40,
    ("custom_components/lipro/core/api/request_policy_support.py", "throttle_change_state"): 75,
    ("custom_components/lipro/core/coordinator/runtime/command_runtime.py", "_execute_device_command"): 65,
    ("custom_components/lipro/core/coordinator/runtime/command_runtime.py", "_verify_delivery"): 35,
}
_ROUTE_TESTS = (
    "tests/meta/governance_followup_route_current_milestones.py",
    "tests/meta/test_governance_bootstrap_smoke.py",
    "tests/meta/test_governance_route_handoff_smoke.py",
    "tests/meta/test_governance_milestone_archives.py",
    "tests/meta/test_version_sync.py",
)

_PHASE75 = "75"
_PHASE75_DIR = "75-access-mode-truth-closure-evidence-promotion-formalization-and-thin-adapter-typing-hardening"


def _function_length(relative_path: str, function_name: str) -> int:
    path = _ROOT / relative_path
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            assert node.end_lineno is not None
            return node.end_lineno - node.lineno + 1
    msg = f"Could not find {function_name} in {relative_path}"
    raise AssertionError(msg)


def test_phase71_hotspot_function_budgets_hold() -> None:
    for (relative_path, function_name), budget in _FUNCTION_BUDGETS.items():
        line_count = _function_length(relative_path, function_name)
        assert line_count <= budget, (
            f"{relative_path}:{function_name} grew beyond Phase 71 budget: {line_count} > {budget}"
        )


def test_phase71_route_tests_use_shared_current_truth_helper() -> None:
    for relative_path in _ROUTE_TESTS:
        text = (_ROOT / relative_path).read_text(encoding="utf-8")
        assert "governance_current_truth" in text


def test_phase71_archived_route_truth_is_distinct_from_latest_v1_20_archive_route() -> None:
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    _assert_latest_archived_route_truth(project_text, roadmap_text, state_text)
    assert LATEST_ARCHIVED_PHASE_TITLE in roadmap_text
    assert f"## Previous Archived Milestone ({PREVIOUS_ARCHIVED_MILESTONE})" in requirements_text
    assert "71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection" in project_text


def test_phase75_context_exists_for_latest_archived_closeout_route() -> None:
    context_path = _ROOT / ".planning" / "phases" / _PHASE75_DIR / f"{_PHASE75}-CONTEXT.md"
    context_text = context_path.read_text(encoding="utf-8")

    assert context_path.exists()
    assert f"# Phase {_PHASE75} Context" in context_text
    assert "v1.19 archived / evidence-ready" in context_text
    assert "runtime_access" in context_text
