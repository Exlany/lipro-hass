"""Focused predecessor guards for Phase 104 service-router/runtime decomposition."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_STATUS,
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
_DEV_ARCH = _ROOT / 'docs' / 'developer_architecture.md'
_PHASE_DIR = _ROOT / '.planning' / 'phases' / '104-service-router-family-split-and-command-runtime-second-pass-decomposition'


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def test_phase104_predecessor_bundle_remains_visible_under_phase105_route() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    verification_text = _read(_VERIFICATION_MATRIX)
    dev_arch_text = _read(_DEV_ARCH)
    verification_doc = _read(_PHASE_DIR / '104-VERIFICATION.md')
    validation_doc = _read(_PHASE_DIR / '104-VALIDATION.md')

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

    assert CURRENT_MILESTONE_STATUS in project_text
    assert CURRENT_MILESTONE_STATUS in roadmap_text
    assert '### Phase 104: Service-router family split and command-runtime second-pass decomposition' in roadmap_text
    assert 'Phase 104 Service-router Family Split / Command-runtime Second-pass Note' in dev_arch_text
    assert '# Phase 104 Verification' in verification_doc
    assert '# Phase 104 Validation Contract' in validation_doc


def test_phase104_maps_and_ledgers_project_new_family_homes() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    residual_text = _read(_RESIDUAL)
    kill_text = _read(_KILL)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)

    for path in (
        'custom_components/lipro/control/service_router_command_handlers.py',
        'custom_components/lipro/control/service_router_schedule_handlers.py',
        'custom_components/lipro/control/service_router_share_handlers.py',
        'custom_components/lipro/control/service_router_diagnostics_handlers.py',
        'custom_components/lipro/control/service_router_maintenance_handlers.py',
        'custom_components/lipro/core/coordinator/runtime/command_runtime_outcome_support.py',
        'tests/meta/test_phase104_service_router_runtime_split_guards.py',
    ):
        assert path in file_matrix_text
    assert 'focused predecessor guard home for Phase 104 service-router/runtime split' in file_matrix_text
    assert '## Phase 104 Residual Delta' in residual_text
    assert '## Phase 104 Status Update' in kill_text
    assert '## Phase 104 Testing Freeze' in testing_text
    assert_testing_inventory_snapshot(testing_text)
    assert '## Phase 104 Service-router Family Split / Command-runtime Second-pass Decomposition' in verification_text


def test_phase104_codeboundaries_keep_thin_index_and_outcome_support_seams() -> None:
    service_router_text = _read(_ROOT / 'custom_components' / 'lipro' / 'control' / 'service_router.py')
    handlers_text = _read(_ROOT / 'custom_components' / 'lipro' / 'control' / 'service_router_handlers.py')
    runtime_text = _read(_ROOT / 'custom_components' / 'lipro' / 'core' / 'coordinator' / 'runtime' / 'command_runtime.py')
    outcome_support_text = _read(_ROOT / 'custom_components' / 'lipro' / 'core' / 'coordinator' / 'runtime' / 'command_runtime_outcome_support.py')

    assert 'from . import service_router_handlers as _handlers, service_router_support as _support' in service_router_text
    assert 'from .service_router_command_handlers import async_handle_send_command' in handlers_text
    assert 'from .service_router_diagnostics_handlers import (' in handlers_text
    assert 'from .service_router_schedule_handlers import (' in handlers_text
    assert 'from .service_router_share_handlers import (' in handlers_text
    assert 'from .service_router_maintenance_handlers import async_handle_refresh_devices' in handlers_text
    assert 'from .command_runtime_outcome_support import (' in runtime_text
    assert 'apply_push_failure' not in runtime_text
    assert 'apply_missing_msg_sn_failure' not in runtime_text
    assert "'_handle_api_error'" in outcome_support_text
    assert "'_record_command_result_failure'" in outcome_support_text
