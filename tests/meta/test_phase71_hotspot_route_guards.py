"""Phase 71 hotspot/function-budget and archived-route truth guards."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_current_truth import (
    CURRENT_MILESTONE,
    CURRENT_MILESTONE_HEADER,
    CURRENT_MILESTONE_LABEL,
    CURRENT_MILESTONE_NAME,
    CURRENT_MILESTONE_ROADMAP_HEADER,
    CURRENT_PHASE_HEADING,
    CURRENT_PHASE_TITLE,
    CURRENT_ROUTE_MODE,
    LATEST_ARCHIVED_EVIDENCE_PATH,
    PREVIOUS_ARCHIVED_PROJECT_HEADER,
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
    "tests/meta/test_governance_release_contract.py",
    "tests/meta/test_governance_milestone_archives.py",
    "tests/meta/test_version_sync.py",
)


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


def test_phase71_archived_route_truth_is_distinct_from_no_active_route() -> None:
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    assert CURRENT_MILESTONE_HEADER in project_text
    assert PREVIOUS_ARCHIVED_PROJECT_HEADER in project_text
    assert CURRENT_MILESTONE_ROADMAP_HEADER in roadmap_text
    assert CURRENT_MILESTONE_HEADER in requirements_text
    assert f"**Current milestone:** `{CURRENT_MILESTONE_LABEL}`" in state_text
    assert f"**Current mode:** `{CURRENT_ROUTE_MODE}`" in state_text
    assert LATEST_ARCHIVED_EVIDENCE_PATH in project_text
    assert LATEST_ARCHIVED_EVIDENCE_PATH in state_text
    assert CURRENT_PHASE_HEADING in roadmap_text
    assert CURRENT_PHASE_TITLE in roadmap_text
    assert f"## Latest Archived Milestone ({CURRENT_MILESTONE})" in requirements_text
    assert "71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection" in project_text
    assert CURRENT_MILESTONE_NAME in state_text
