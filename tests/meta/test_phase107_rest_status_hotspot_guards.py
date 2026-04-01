"""Focused predecessor guards for Phase 107 REST/auth/status hotspot convergence."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot
from .governance_current_truth import CURRENT_MILESTONE_DEFAULT_NEXT, CURRENT_ROUTE

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
_REST = _ROOT / 'custom_components' / 'lipro' / 'core' / 'api' / 'rest_facade.py'
_STATUS_SUPPORT = _ROOT / 'custom_components' / 'lipro' / 'core' / 'api' / 'status_fallback_support.py'
_REQUEST_POLICY_SUPPORT = _ROOT / 'custom_components' / 'lipro' / 'core' / 'api' / 'request_policy_support.py'
_PHASE_DIR = _ROOT / '.planning' / 'phases' / '107-rest-auth-status-hotspot-convergence-and-support-surface-slimming'


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def test_phase107_predecessor_bundle_remains_visible_under_phase109_route() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    verification_text = _read(_VERIFICATION_MATRIX)
    dev_arch_text = _read(_DEV_ARCH)
    verification_doc = _read(_PHASE_DIR / '107-VERIFICATION.md')
    validation_doc = _read(_PHASE_DIR / '107-VALIDATION.md')

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

    assert '### Phase 107: REST/auth/status hotspot convergence and support-surface slimming' in roadmap_text
    assert 'Phase 107 REST/Auth/Status Hotspot Convergence Note' in dev_arch_text
    assert '# Phase 107 Verification' in verification_doc
    assert '# Phase 107 Validation Contract' in validation_doc


def test_phase107_ledgers_testing_and_file_matrix_freeze_predecessor_story() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    residual_text = _read(_RESIDUAL)
    kill_text = _read(_KILL)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)

    for path in (
        'custom_components/lipro/core/api/rest_facade.py',
        'custom_components/lipro/core/api/status_fallback_support.py',
        'custom_components/lipro/core/api/request_policy_support.py',
        'tests/meta/test_phase107_rest_status_hotspot_guards.py',
    ):
        assert path in file_matrix_text
    assert 'focused predecessor guard home for Phase 107 REST/auth/status hotspot convergence' in file_matrix_text
    assert '## Phase 107 Residual Delta' in residual_text
    assert '## Phase 107 Status Update' in kill_text
    assert '## Phase 107 Testing Freeze' in testing_text
    assert_testing_inventory_snapshot(testing_text)
    assert '## Phase 107 REST/Auth/Status Hotspot Convergence / Support-surface Slimming' in verification_text
    for token in (
        '$gsd-discuss-phase 110',
        'tests/meta/test_phase107_rest_status_hotspot_guards.py',
        '.planning/phases/107-rest-auth-status-hotspot-convergence-and-support-surface-slimming/{107-01-SUMMARY.md,107-02-SUMMARY.md,107-03-SUMMARY.md,107-VERIFICATION.md,107-VALIDATION.md}',
    ):
        assert token in verification_text


def test_phase107_code_boundaries_keep_formal_and_support_homes_visible() -> None:
    rest_text = _read(_REST)
    status_support_text = _read(_STATUS_SUPPORT)
    request_policy_text = _read(_REQUEST_POLICY_SUPPORT)

    for token in (
        'def _build_endpoint_surface(self) -> RestEndpointSurface:',
        'def _build_request_gateway(self) -> RestRequestGateway:',
        'def auth_api(self) -> AuthApiService:',
    ):
        assert token in rest_text

    for token in (
        'class _BinarySplitQueryContext:',
        'class _BinarySplitAccumulator:',
        'from .status_fallback_split_executor import (',
        'execute_batch_fallback_query,',
        'execute_binary_split_query,',
        'async def _query_items_individually(',
        'def _split_subset_ids(subset: list[str]) -> tuple[list[str], list[str]]:',
        'async def _query_binary_split_root(',
        'async def query_items_by_binary_split_impl(',
        'async def query_with_fallback_impl(',
    ):
        assert token in status_support_text

    for token in (
        'class _CommandPacingCaches:',
        'def enforce_limit(self) -> None:',
        'def _build_command_pacing_caches(',
        'async def record_change_state_busy(',
        'async def record_change_state_success(',
        'async def throttle_change_state(',
    ):
        assert token in request_policy_text
