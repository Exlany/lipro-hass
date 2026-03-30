"""Focused latest-archived guards for Phase 105 governance freeze visibility."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_ROUTE,
    PREVIOUS_ARCHIVED_PROJECT_HEADER,
)
from .governance_promoted_assets import _assert_exact_promoted_phase_assets

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
_DEV_ARCH = _ROOT / 'docs' / 'developer_architecture.md'
_PHASE_DIR = _ROOT / '.planning' / 'phases' / '105-governance-rule-datafication-and-milestone-freeze'
_PROMOTED = '105-governance-rule-datafication-and-milestone-freeze'


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')



def test_phase105_latest_archived_bundle_remains_visible_under_phase109_route() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    verification_text = _read(_VERIFICATION_MATRIX)
    dev_arch_text = _read(_DEV_ARCH)
    verification_doc = _read(_PHASE_DIR / '105-VERIFICATION.md')
    validation_doc = _read(_PHASE_DIR / '105-VALIDATION.md')

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

    assert PREVIOUS_ARCHIVED_PROJECT_HEADER in project_text
    assert '### Phase 105: Governance rule datafication and milestone freeze' in roadmap_text
    assert 'Phase 105 Governance Rule Datafication / Milestone Freeze Note' in dev_arch_text
    assert '# Phase 105 Verification' in verification_doc
    assert '# Phase 105 Validation Contract' in validation_doc


def test_phase105_ledgers_testing_and_promoted_assets_freeze_the_same_story() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    residual_text = _read(_RESIDUAL)
    kill_text = _read(_KILL)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)

    _assert_exact_promoted_phase_assets(
        _PROMOTED,
        '105-01-SUMMARY.md',
        '105-02-SUMMARY.md',
        '105-03-SUMMARY.md',
        '105-SUMMARY.md',
        '105-VERIFICATION.md',
        '105-VALIDATION.md',
    )

    for path in (
        'tests/meta/governance_followup_route_specs.py',
        'tests/meta/test_phase104_service_router_runtime_split_guards.py',
        'tests/meta/test_phase105_governance_freeze_guards.py',
    ):
        assert path in file_matrix_text
    assert 'focused latest-archived closeout guard home for Phase 105 governance freeze' in file_matrix_text
    assert '## Phase 105 Residual Delta' in residual_text
    assert '## Phase 105 Status Update' in kill_text
    assert '## Phase 105 Testing Freeze' in testing_text
    assert_testing_inventory_snapshot(testing_text)
    assert '## Phase 105 Governance Rule Datafication / Milestone Freeze' in verification_text
    for token in (
        '$gsd-discuss-phase 110',
        '.planning/reviews/PROMOTED_PHASE_ASSETS.md',
        'tests/meta/test_phase105_governance_freeze_guards.py',
        'tests/meta/governance_followup_route_specs.py',
    ):
        assert token in verification_text
