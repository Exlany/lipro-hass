"""Focused predecessor guards for Phase 109 anonymous-share manager inward decomposition."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_HEADER,
    CURRENT_ROUTE,
)

_ROOT = repo_root(Path(__file__))
_PROJECT = _ROOT / '.planning' / 'PROJECT.md'
_ROADMAP = _ROOT / '.planning' / 'ROADMAP.md'
_REQUIREMENTS = _ROOT / '.planning' / 'REQUIREMENTS.md'
_STATE = _ROOT / '.planning' / 'STATE.md'
_MILESTONES = _ROOT / '.planning' / 'MILESTONES.md'
_VERIFICATION_MATRIX = _ROOT / '.planning' / 'baseline' / 'VERIFICATION_MATRIX.md'
_FILE_MATRIX = _ROOT / '.planning' / 'reviews' / 'FILE_MATRIX.md'
_RESIDUAL = _ROOT / '.planning' / 'reviews' / 'RESIDUAL_LEDGER.md'
_KILL = _ROOT / '.planning' / 'reviews' / 'KILL_LIST.md'
_TESTING = _ROOT / '.planning' / 'codebase' / 'TESTING.md'
_DEV_ARCH = _ROOT / 'docs' / 'architecture_archive.md'
_MANAGER = _ROOT / 'custom_components' / 'lipro' / 'core' / 'anonymous_share' / 'manager.py'
_MANAGER_SCOPE = _ROOT / 'custom_components' / 'lipro' / 'core' / 'anonymous_share' / 'manager_scope.py'
_MANAGER_SUPPORT = _ROOT / 'custom_components' / 'lipro' / 'core' / 'anonymous_share' / 'manager_support.py'
_SCOPE_TEST = _ROOT / 'tests' / 'core' / 'anonymous_share' / 'test_manager_scope_views.py'
_PHASE_DIR = _ROOT / '.planning' / 'phases' / '109-anonymous-share-manager-inward-decomposition'


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def test_phase109_predecessor_bundle_remains_visible_under_phase110_route() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    verification_text = _read(_VERIFICATION_MATRIX)
    dev_arch_text = _read(_DEV_ARCH)
    verification_doc = _read(_PHASE_DIR / '109-VERIFICATION.md')
    validation_doc = _read(_PHASE_DIR / '109-VALIDATION.md')

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

    assert '### Phase 109: Anonymous-share manager inward decomposition' in roadmap_text
    assert CURRENT_MILESTONE_HEADER in project_text
    assert CURRENT_MILESTONE_HEADER in requirements_text
    assert CURRENT_MILESTONE_HEADER in milestones_text
    assert 'Phase 109 Anonymous-share Manager Inward Decomposition Note' in dev_arch_text
    assert '# Phase 109 Verification' in verification_doc
    assert '# Phase 109 Validation Contract' in validation_doc


def test_phase109_ledgers_testing_and_file_matrix_freeze_predecessor_story() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    residual_text = _read(_RESIDUAL)
    kill_text = _read(_KILL)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)

    for path in (
        'custom_components/lipro/core/anonymous_share/manager.py',
        'custom_components/lipro/core/anonymous_share/manager_scope.py',
        'custom_components/lipro/core/anonymous_share/manager_support.py',
        'tests/core/anonymous_share/test_manager_scope_views.py',
        'tests/meta/test_phase109_anonymous_share_manager_inward_decomposition_guards.py',
    ):
        assert path in file_matrix_text
    assert 'focused predecessor guard home for Phase 109 anonymous-share manager inward decomposition' in file_matrix_text
    assert '## Phase 109 Residual Delta' in residual_text
    assert '## Phase 109 Status Update' in kill_text
    assert '## Phase 109 Testing Freeze' in testing_text
    assert_testing_inventory_snapshot(testing_text)
    assert '## Phase 109 Anonymous-share Manager Inward Decomposition' in verification_text
    for token in (
        CURRENT_MILESTONE_DEFAULT_NEXT,
        'tests/meta/test_phase109_anonymous_share_manager_inward_decomposition_guards.py',
        '.planning/phases/109-anonymous-share-manager-inward-decomposition/{109-01-SUMMARY.md,109-02-SUMMARY.md,109-03-SUMMARY.md,109-VERIFICATION.md,109-VALIDATION.md}',
    ):
        assert token in verification_text


def test_phase109_code_boundaries_keep_single_outward_manager_home() -> None:
    manager_text = _read(_MANAGER)
    manager_scope_text = _read(_MANAGER_SCOPE)
    manager_support_text = _read(_MANAGER_SUPPORT)
    scope_test_text = _read(_SCOPE_TEST)

    for token in (
        'self._scope_views = AnonymousShareScopeViews(',
        'return self._scope_views.for_scope(scope_key)',
        'return build_pending_report_payload(',
        'finalize_successful_submit_state,',
    ):
        assert token in manager_text

    for token in (
        'class AnonymousShareScopeViews:',
        'def primary_manager(',
        'def aggregate_pending_count(',
    ):
        assert token in manager_scope_text

    for token in (
        'def build_pending_report_payload(',
        'def finalize_successful_submit_state(',
    ):
        assert token in manager_support_text

    for token in (
        'def test_for_scope_caches_manager_instances() -> None:',
        'def test_primary_manager_prefers_enabled_scope() -> None:',
        'def test_aggregate_pending_count_sums_scoped_errors() -> None:',
    ):
        assert token in scope_test_text
