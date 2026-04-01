"""Focused closeout guards for Phase 124 auth/flow/schedule contract closure."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_PLAN_COUNT,
    CURRENT_MILESTONE_STATUS,
    CURRENT_MILESTONE_SUMMARY_COUNT,
    CURRENT_PHASE_HEADING,
    CURRENT_ROUTE,
)

_ROOT = repo_root(Path(__file__))
_PROJECT = _ROOT / ".planning" / "PROJECT.md"
_ROADMAP = _ROOT / ".planning" / "ROADMAP.md"
_REQUIREMENTS = _ROOT / ".planning" / "REQUIREMENTS.md"
_STATE = _ROOT / ".planning" / "STATE.md"
_MILESTONES = _ROOT / ".planning" / "MILESTONES.md"
_PUBLIC_SURFACES = _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
_DEPENDENCY_MATRIX = _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
_VERIFICATION_MATRIX = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_RESIDUAL = _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
_KILL = _ROOT / ".planning" / "reviews" / "KILL_LIST.md"
_AUDIT_LEDGER = _ROOT / ".planning" / "reviews" / "V1_35_MASTER_AUDIT_LEDGER.md"
_ARCHITECTURE = _ROOT / ".planning" / "codebase" / "ARCHITECTURE.md"
_CONCERNS = _ROOT / ".planning" / "codebase" / "CONCERNS.md"
_TESTING = _ROOT / ".planning" / "codebase" / "TESTING.md"
_DEV_ARCH = _ROOT / "docs" / "developer_architecture.md"
_CHANGELOG = _ROOT / "CHANGELOG.md"
_PHASE_DIR = _ROOT / ".planning/phases/124-config-entry-auth-seed-normalization-config-flow-adapter-thinning-and-schedule-contract-closure"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase124_route_truth_and_closeout_assets_are_current() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    phase_summary = _read(_PHASE_DIR / "124-SUMMARY.md")
    verification = _read(_PHASE_DIR / "124-VERIFICATION.md")

    for text in (project_text, roadmap_text, requirements_text, state_text, milestones_text):
        assert CURRENT_ROUTE in text
        assert CURRENT_MILESTONE_DEFAULT_NEXT in text
        assert CURRENT_MILESTONE_STATUS in text
    assert CURRENT_PHASE_HEADING in roadmap_text
    assert CURRENT_MILESTONE_PLAN_COUNT == 5
    assert CURRENT_MILESTONE_SUMMARY_COUNT == 6
    for name in (
        "124-01-SUMMARY.md",
        "124-02-SUMMARY.md",
        "124-03-SUMMARY.md",
        "124-04-SUMMARY.md",
        "124-05-SUMMARY.md",
    ):
        assert (_PHASE_DIR / name).exists()
    assert "# Phase 124 Summary" in phase_summary
    assert "# Phase 124 Verification" in verification


def test_phase124_governance_maps_and_ledgers_project_closeout_truth() -> None:
    public_surfaces_text = _read(_PUBLIC_SURFACES)
    dependency_text = _read(_DEPENDENCY_MATRIX)
    verification_text = _read(_VERIFICATION_MATRIX)
    file_matrix_text = _read(_FILE_MATRIX)
    residual_text = _read(_RESIDUAL)
    kill_text = _read(_KILL)
    audit_text = _read(_AUDIT_LEDGER)
    architecture_text = _read(_ARCHITECTURE)
    concerns_text = _read(_CONCERNS)
    testing_text = _read(_TESTING)
    dev_arch_text = _read(_DEV_ARCH)
    changelog_text = _read(_CHANGELOG)

    assert "## Phase 124 Auth/Flow/Schedule Clarifications" in public_surfaces_text
    assert "## Phase 124 Auth/Flow/Schedule Dependency Clarifications" in dependency_text
    assert "## Phase 124 Exit Contract" in verification_text
    assert "## Phase 124 Residual Delta" in residual_text
    assert "## Phase 124 Status Update" in kill_text
    assert "## Phase 124 Final Carry-forward Closure" in audit_text
    assert "## Phase 124 Closure Notes" in architecture_text
    assert "## Phase 124 Concern Update" in concerns_text
    assert "## Phase 124 Testing Freeze" in testing_text
    assert "## Phase 124 Closeout Notes" in dev_arch_text
    assert "Phase 124" in changelog_text
    assert_testing_inventory_snapshot(testing_text)
    for token in (
        "custom_components/lipro/flow/step_handlers.py",
        "custom_components/lipro/services/contracts.py",
        "custom_components/lipro/services/schedule.py",
        "tests/meta/test_phase124_flow_auth_schedule_contract_guards.py",
    ):
        assert token in file_matrix_text


def test_phase124_codeboundaries_keep_single_flow_auth_schedule_truth() -> None:
    config_flow_text = _read(_ROOT / "custom_components" / "lipro" / "config_flow.py")
    entry_auth_text = _read(_ROOT / "custom_components" / "lipro" / "entry_auth.py")
    login_text = _read(_ROOT / "custom_components" / "lipro" / "flow" / "login.py")
    submission_text = _read(_ROOT / "custom_components" / "lipro" / "flow" / "submission.py")
    contracts_text = _read(_ROOT / "custom_components" / "lipro" / "services" / "contracts.py")
    schedule_text = _read(_ROOT / "custom_components" / "lipro" / "services" / "schedule.py")
    en_text = _read(_ROOT / "custom_components" / "lipro" / "translations" / "en.json")
    zh_text = _read(_ROOT / "custom_components" / "lipro" / "translations" / "zh-Hans.json")

    assert "from .flow.step_handlers import (" in config_flow_text
    assert "return await _async_handle_user_step(self, user_input, logger=_LOGGER)" in config_flow_text
    assert "return await _async_handle_reauth_confirm_step(" in config_flow_text
    assert "return await _async_handle_reconfigure_step(" in config_flow_text

    for token in (
        "EntryCredentialSeedState",
        "resolve_entry_credential_seed_state",
        "apply_entry_credential_seed_state",
        "persist_entry_tokens_if_changed",
    ):
        assert token in entry_auth_text

    assert "apply_entry_credential_seed_state" in login_text
    assert "resolve_entry_remember_password_hash(" in submission_text

    for token in (
        "NormalizedScheduleRow",
        "GetSchedulesResult",
        "AddScheduleResult",
        "DeleteSchedulesResult",
        "normalize_get_schedules_payload",
        "normalize_add_schedule_payload",
        "normalize_delete_schedules_payload",
    ):
        assert token in contracts_text
        assert token in schedule_text

    assert 'translation_key="invalid_schedule_request"' in schedule_text
    assert '"invalid_schedule_request"' in en_text
    assert '"invalid_schedule_request"' in zh_text
