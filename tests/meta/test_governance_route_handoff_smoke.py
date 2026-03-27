"""Focused route-handoff smoke guards for archived-only fast paths."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

from tests.helpers.repo_root import repo_root

from .conftest import _as_bool, _as_mapping, _as_mapping_list, _as_str
from .governance_contract_helpers import _assert_latest_archived_route_truth
from .governance_current_truth import (
    CURRENT_MILESTONE,
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_STATUS,
    CURRENT_ROUTE,
    LATEST_ARCHIVED_EVIDENCE_PATH,
)
from .governance_promoted_assets import _assert_promoted_phase_assets

_ROOT = repo_root(Path(__file__))
_GSD_TOOLS = Path.home() / '.codex' / 'get-shit-done' / 'bin' / 'gsd-tools.cjs'


def _run_gsd_tools(*args: str) -> dict[str, object]:
    node_executable = shutil.which('node')
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
    if payload.startswith('@file:'):
        payload = Path(payload.removeprefix('@file:')).read_text(encoding='utf-8')
    loaded = json.loads(payload)
    assert isinstance(loaded, dict)
    return loaded


def test_route_handoff_docs_and_ledgers_stay_in_sync() -> None:
    project_text = (_ROOT / '.planning' / 'PROJECT.md').read_text(encoding='utf-8')
    roadmap_text = (_ROOT / '.planning' / 'ROADMAP.md').read_text(encoding='utf-8')
    requirements_text = (_ROOT / '.planning' / 'REQUIREMENTS.md').read_text(encoding='utf-8')
    state_text = (_ROOT / '.planning' / 'STATE.md').read_text(encoding='utf-8')
    verification_text = (
        _ROOT / '.planning' / 'baseline' / 'VERIFICATION_MATRIX.md'
    ).read_text(encoding='utf-8')
    file_matrix_text = (
        _ROOT / '.planning' / 'reviews' / 'FILE_MATRIX.md'
    ).read_text(encoding='utf-8')

    _assert_latest_archived_route_truth(project_text, roadmap_text, state_text)

    assert CURRENT_ROUTE in project_text
    assert CURRENT_MILESTONE_STATUS in project_text
    assert CURRENT_MILESTONE_STATUS in roadmap_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in project_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in roadmap_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in state_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in requirements_text
    assert '## Phase 88 Governance Sync / Quality Proof / Milestone Freeze' in verification_text
    assert CURRENT_ROUTE in verification_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in verification_text
    assert LATEST_ARCHIVED_EVIDENCE_PATH in verification_text
    assert 'tests/meta/test_governance_route_handoff_smoke.py' in verification_text
    assert 'tests/meta/test_governance_route_handoff_smoke.py' in file_matrix_text
    assert 'route-handoff gsd fast-path smoke guard home' in file_matrix_text


def test_gsd_fast_path_matches_current_active_route_story() -> None:
    progress = _run_gsd_tools('init', 'progress')
    phases = _as_mapping_list(progress['phases'])
    phase_85 = next(phase for phase in phases if _as_str(phase['number']) == '85')
    phase_85_plan_count = phase_85['plan_count']
    phase_85_summary_count = phase_85['summary_count']
    assert isinstance(phase_85_plan_count, int)
    assert isinstance(phase_85_summary_count, int)
    assert phase_85_plan_count == 3
    assert phase_85_summary_count == 3
    assert _as_str(phase_85['status']) == 'complete'

    phase_index = _run_gsd_tools('phase-plan-index', '85')
    assert _as_str(phase_index['phase']) == '85'
    plans = _as_mapping_list(phase_index['plans'])
    assert [_as_str(plan['id']) for plan in plans] == ['85-01', '85-02', '85-03']
    assert phase_85_summary_count == sum(
        1 for plan in plans if _as_bool(plan['has_summary']) is True
    )
    assert phase_index['incomplete'] == []

    state = _run_gsd_tools('state', 'json')
    assert _as_str(state['milestone']) == CURRENT_MILESTONE
    assert _as_str(state['status']) == 'archived'
    assert _as_mapping(state['progress']) == {
        'total_phases': '4',
        'completed_phases': '4',
        'total_plans': '14',
        'completed_plans': '14',
    }
    assert progress['phase_count'] == len(phases)
    assert progress['completed_count'] == 4
    assert progress['current_phase'] is None
    assert progress['next_phase'] is None

    plan_init = _run_gsd_tools('init', 'plan-phase', '88')
    assert _as_bool(plan_init['phase_found']) is True
    assert _as_str(plan_init['phase_number']) == '88'
    assert _as_bool(plan_init['has_plans']) is True
    assert _as_bool(plan_init['has_research']) is True
    assert plan_init['plan_count'] == 3

    phase_86 = next(phase for phase in phases if _as_str(phase['number']) == '86')
    assert _as_str(phase_86['status']) == 'complete'
    assert phase_86['plan_count'] == 4
    assert phase_86['summary_count'] == 4

    phase_86_index = _run_gsd_tools('phase-plan-index', '86')
    assert _as_str(phase_86_index['phase']) == '86'
    phase_86_plans = _as_mapping_list(phase_86_index['plans'])
    assert [_as_str(plan['id']) for plan in phase_86_plans] == ['86-01', '86-02', '86-03', '86-04']
    assert phase_86_index['incomplete'] == []

    phase_87 = next(phase for phase in phases if _as_str(phase['number']) == '87')
    assert _as_str(phase_87['status']) == 'complete'
    assert phase_87['plan_count'] == 4
    assert phase_87['summary_count'] == 4

    phase_87_index = _run_gsd_tools('phase-plan-index', '87')
    assert _as_str(phase_87_index['phase']) == '87'
    phase_87_plans = _as_mapping_list(phase_87_index['plans'])
    assert [_as_str(plan['id']) for plan in phase_87_plans] == ['87-01', '87-02', '87-03', '87-04']
    assert phase_87_index['incomplete'] == []

    phase_88 = next(phase for phase in phases if _as_str(phase['number']) == '88')
    assert _as_str(phase_88['status']) == 'complete'
    assert phase_88['plan_count'] == 3
    assert phase_88['summary_count'] == 4

    phase_88_index = _run_gsd_tools('phase-plan-index', '88')
    assert _as_str(phase_88_index['phase']) == '88'
    phase_88_plans = _as_mapping_list(phase_88_index['plans'])
    assert [_as_str(plan['id']) for plan in phase_88_plans] == ['88-01', '88-02', '88-03']
    assert phase_88_index['incomplete'] == []


def test_recent_governance_closeout_assets_are_promoted_without_planning_traces() -> None:
    _assert_promoted_phase_assets(
        '76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation',
        '76-01-SUMMARY.md',
        '76-02-SUMMARY.md',
        '76-03-SUMMARY.md',
        '76-VERIFICATION.md',
        '76-VALIDATION.md',
    )
    _assert_promoted_phase_assets(
        '77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction',
        '77-01-SUMMARY.md',
        '77-02-SUMMARY.md',
        '77-03-SUMMARY.md',
        '77-VERIFICATION.md',
        '77-VALIDATION.md',
    )
    _assert_promoted_phase_assets(
        '78-quality-gate-formalization-route-handoff-ergonomics-and-milestone-closeout-readiness',
        '78-01-SUMMARY.md',
        '78-02-SUMMARY.md',
        '78-03-SUMMARY.md',
        '78-SUMMARY.md',
        '78-VERIFICATION.md',
        '78-VALIDATION.md',
    )
    _assert_promoted_phase_assets(
        '79-governance-tooling-hotspot-decomposition-and-release-contract-topicization',
        '79-01-SUMMARY.md',
        '79-02-SUMMARY.md',
        '79-03-SUMMARY.md',
        '79-SUMMARY.md',
        '79-VERIFICATION.md',
        '79-VALIDATION.md',
    )
    _assert_promoted_phase_assets(
        '80-governance-typing-closure-and-final-meta-suite-hotspot-topicization',
        '80-01-SUMMARY.md',
        '80-02-SUMMARY.md',
        '80-03-SUMMARY.md',
        '80-SUMMARY.md',
        '80-VERIFICATION.md',
        '80-VALIDATION.md',
    )
    _assert_promoted_phase_assets(
        '81-contributor-onramp-route-convergence-and-public-entry-contract',
        '81-01-SUMMARY.md',
        '81-02-SUMMARY.md',
        '81-03-SUMMARY.md',
        '81-SUMMARY.md',
        '81-VERIFICATION.md',
        '81-VALIDATION.md',
    )
    _assert_promoted_phase_assets(
        '82-release-operations-closure-and-evidence-chain-formalization',
        '82-01-SUMMARY.md',
        '82-02-SUMMARY.md',
        '82-03-SUMMARY.md',
        '82-SUMMARY.md',
        '82-VERIFICATION.md',
        '82-VALIDATION.md',
    )
    _assert_promoted_phase_assets(
        '83-intake-templates-and-maintainer-stewardship-contract',
        '83-01-SUMMARY.md',
        '83-02-SUMMARY.md',
        '83-03-SUMMARY.md',
        '83-SUMMARY.md',
        '83-VERIFICATION.md',
        '83-VALIDATION.md',
    )
    _assert_promoted_phase_assets(
        '84-governance-open-source-guard-coverage-and-milestone-truth-freeze',
        '84-01-SUMMARY.md',
        '84-02-SUMMARY.md',
        '84-03-SUMMARY.md',
        '84-SUMMARY.md',
        '84-VERIFICATION.md',
        '84-VALIDATION.md',
    )
    _assert_promoted_phase_assets(
        '88-governance-sync-quality-proof-and-milestone-freeze',
        '88-01-SUMMARY.md',
        '88-02-SUMMARY.md',
        '88-03-SUMMARY.md',
        '88-SUMMARY.md',
        '88-VERIFICATION.md',
        '88-VALIDATION.md',
    )
