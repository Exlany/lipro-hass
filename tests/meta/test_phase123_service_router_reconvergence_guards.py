"""Focused closeout guards for Phase 123 service-router reconvergence."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_STATUS,
    CURRENT_PHASE_HEADING,
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
_PHASE_DIR = _ROOT / '.planning/phases/123-service-router-family-reconvergence-control-plane-locality-and-public-architecture-hygiene'


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def test_phase123_route_truth_and_assets_are_current() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    verification_doc = _read(_PHASE_DIR / '123-VERIFICATION.md')

    for text in (
        project_text,
        roadmap_text,
        requirements_text,
        state_text,
        milestones_text,
    ):
        assert CURRENT_ROUTE in text
        assert CURRENT_MILESTONE_DEFAULT_NEXT in text
    assert CURRENT_MILESTONE_STATUS in project_text
    assert CURRENT_MILESTONE_STATUS in roadmap_text
    assert CURRENT_PHASE_HEADING in roadmap_text
    assert '# Phase 123 Verification' in verification_doc


def test_phase123_maps_and_ledgers_project_reconverged_service_router_truth() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    residual_text = _read(_RESIDUAL)
    kill_text = _read(_KILL)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)

    for path in (
        'custom_components/lipro/control/service_router_handlers.py',
        'custom_components/lipro/control/service_router_diagnostics_handlers.py',
        'tests/meta/test_phase123_service_router_reconvergence_guards.py',
    ):
        assert path in file_matrix_text
    for path in (
        'custom_components/lipro/control/service_router_command_handlers.py',
        'custom_components/lipro/control/service_router_schedule_handlers.py',
        'custom_components/lipro/control/service_router_share_handlers.py',
        'custom_components/lipro/control/service_router_maintenance_handlers.py',
    ):
        assert path not in file_matrix_text
    assert 'control-local callback family home for command/schedule/share/maintenance service-router handlers' in file_matrix_text
    assert '## Phase 123 Residual Delta' in residual_text
    assert '## Phase 123 Status Update' in kill_text
    assert '## Phase 123 Testing Freeze' in testing_text
    assert_testing_inventory_snapshot(testing_text)
    assert '## Phase 123 Service-router Reconvergence / Control-plane Locality Tightening' in verification_text


def test_phase123_codeboundaries_keep_single_non_diagnostics_handler_home() -> None:
    service_router_text = _read(_ROOT / 'custom_components' / 'lipro' / 'control' / 'service_router.py')
    handlers_text = _read(_ROOT / 'custom_components' / 'lipro' / 'control' / 'service_router_handlers.py')

    assert 'from . import service_router_handlers as _handlers, service_router_support as _support' in service_router_text
    assert 'from .service_router_command_handlers import' not in handlers_text
    assert 'from .service_router_schedule_handlers import' not in handlers_text
    assert 'from .service_router_share_handlers import' not in handlers_text
    assert 'from .service_router_maintenance_handlers import' not in handlers_text
    assert 'from .service_router_diagnostics_handlers import (' in handlers_text
    for token in (
        '_async_handle_send_command_service',
        '_async_handle_add_schedule_service',
        '_async_handle_submit_anonymous_share_service',
        '_async_handle_refresh_devices_service',
    ):
        assert token in handlers_text
    for path in (
        _ROOT / 'custom_components' / 'lipro' / 'control' / 'service_router_command_handlers.py',
        _ROOT / 'custom_components' / 'lipro' / 'control' / 'service_router_schedule_handlers.py',
        _ROOT / 'custom_components' / 'lipro' / 'control' / 'service_router_share_handlers.py',
        _ROOT / 'custom_components' / 'lipro' / 'control' / 'service_router_maintenance_handlers.py',
    ):
        assert not path.exists()
