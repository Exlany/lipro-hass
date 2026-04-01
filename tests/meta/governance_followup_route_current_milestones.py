"""Current-milestone and continuity truth guards for the active v1.35 route."""

from __future__ import annotations

from .governance_contract_helpers import _assert_current_route_truth
from .governance_current_truth import (
    CURRENT_MILESTONE_COMPLETED_PLAN_COUNT,
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_HEADER,
    CURRENT_MILESTONE_ROADMAP_HEADER,
    CURRENT_MILESTONE_STATE_LABEL,
    CURRENT_MILESTONE_STATUS,
    CURRENT_MILESTONE_TOTAL_PLAN_COUNT,
    CURRENT_PHASE,
    CURRENT_PHASE_HEADING,
    CURRENT_ROUTE_MODE,
    HAS_ACTIVE_MILESTONE,
    LATEST_ARCHIVED_AUDIT_PATH,
    LATEST_ARCHIVED_EVIDENCE_PATH,
    LATEST_ARCHIVED_MILESTONE,
    LATEST_ARCHIVED_PROJECT_HEADER,
    PREVIOUS_ARCHIVED_PROJECT_HEADER,
    _as_mapping,
    _as_optional_mapping,
    assert_machine_readable_route_contracts,
)
from .governance_followup_route_specs import (
    assert_contains_all,
    assert_not_contains_any,
    load_planning_docs_snapshot,
)

_SNAPSHOT = load_planning_docs_snapshot()
_MILESTONES_TEXT = _SNAPSHOT.milestones
_ROADMAP_TEXT = _SNAPSHOT.roadmap
_REQUIREMENTS_TEXT = _SNAPSHOT.requirements
_PROJECT_TEXT = _SNAPSHOT.project
_STATE_TEXT = _SNAPSHOT.state


def test_machine_readable_route_contracts_point_to_active_v1_35_phase_125() -> None:
    contracts = assert_machine_readable_route_contracts()
    for doc_name in ('PROJECT', 'ROADMAP', 'REQUIREMENTS', 'STATE', 'MILESTONES'):
        contract = _as_mapping(contracts[doc_name])
        active = _as_optional_mapping(contract['active_milestone'])
        latest_archived = _as_mapping(contract['latest_archived'])
        previous_archived = _as_mapping(contract['previous_archived'])
        bootstrap = _as_mapping(contract['bootstrap'])

        assert active is not None, doc_name
        assert active['version'] == 'v1.35'
        assert active['phase'] == CURRENT_PHASE
        assert active['status'] == CURRENT_MILESTONE_STATUS
        assert latest_archived['version'] == 'v1.34'
        assert latest_archived['phase'] == '121'
        assert latest_archived['status'] == 'archived / evidence-ready (2026-04-01)'
        assert previous_archived['version'] == 'v1.33'
        assert bootstrap['current_route'] == CURRENT_ROUTE_MODE
        assert bootstrap['default_next_command'] == CURRENT_MILESTONE_DEFAULT_NEXT
        assert bootstrap['latest_archived_evidence_pointer'] == LATEST_ARCHIVED_EVIDENCE_PATH


def test_active_v1_35_truth_is_reflected_in_live_docs() -> None:
    _assert_current_route_truth(_PROJECT_TEXT, _ROADMAP_TEXT, _STATE_TEXT)

    assert HAS_ACTIVE_MILESTONE is True
    assert_contains_all(
        _PROJECT_TEXT,
        CURRENT_MILESTONE_HEADER,
        LATEST_ARCHIVED_PROJECT_HEADER,
        PREVIOUS_ARCHIVED_PROJECT_HEADER,
        f'**Current status:** `{CURRENT_MILESTONE_STATUS}`',
        f'**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`',
        'runtime_types.py',
        'config_flow.py',
        'entry_auth.py',
        'machine-readable contract',
    )
    assert_contains_all(
        _ROADMAP_TEXT,
        CURRENT_MILESTONE_ROADMAP_HEADER,
        f'**Milestone status:** `{CURRENT_MILESTONE_STATUS}`',
        f'**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`',
        CURRENT_PHASE_HEADING,
        '## Phases',
        'Phase 122',
        'Phase 123',
        'Phase 124',
        'Phase 125',
        '## Progress',
    )
    assert_contains_all(
        _STATE_TEXT,
        f'**Current milestone:** `{CURRENT_MILESTONE_STATE_LABEL}`',
        f'**Current mode:** `{CURRENT_ROUTE_MODE}`',
        f'- **Phase:** `{CURRENT_PHASE} of {CURRENT_PHASE}`',
        f'- **Plan:** `{CURRENT_MILESTONE_COMPLETED_PLAN_COUNT} of {CURRENT_MILESTONE_TOTAL_PLAN_COUNT}`',
        '- **Status:** `complete; closeout-ready`',
        '## Recommended Next Command',
        CURRENT_MILESTONE_DEFAULT_NEXT,
        'closeout-ready',
    )


def test_v1_35_requirements_traceability_and_coverage_include_phase_125() -> None:
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        '- [x] **AUD-05**',
        '- [x] **DOC-12**',
        '- [x] **OSS-16**',
        '- [x] **GOV-81**',
        '- [x] **TST-44**',
        '- [x] **ARC-34**',
        '- [x] **HOT-54**',
        '- [x] **DOC-13**',
        '- [x] **GOV-82**',
        '- [x] **TST-45**',
        '- [x] **ARC-35**',
        '- [x] **HOT-55**',
        '- [x] **ARC-36**',
        '- [x] **GOV-83**',
        '- [x] **TST-46**',
        '- [x] **ARC-37**',
        '- [x] **HOT-56**',
        '- [x] **GOV-84**',
        '- [x] **TST-47**',
        '- [x] **QLT-49**',
        '- [x] **DOC-14**',
        '| ARC-37 | Phase 125 | Complete |',
        '| HOT-56 | Phase 125 | Complete |',
        '| GOV-84 | Phase 125 | Complete |',
        '| TST-47 | Phase 125 | Complete |',
        '| QLT-49 | Phase 125 | Complete |',
        '| DOC-14 | Phase 125 | Complete |',
        '- v1.35 requirements: 21 total',
        '- Mapped to phases: 21',
        '- Complete: 21',
        '- Pending: 0',
        f'**Milestone status:** `{CURRENT_MILESTONE_STATUS}`',
        f'**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`',
        f'**Latest archived baseline:** `{LATEST_ARCHIVED_MILESTONE}`',
        f'**Archive pointer:** `{LATEST_ARCHIVED_EVIDENCE_PATH}`',
        f'**Latest archived audit artifact:** `{LATEST_ARCHIVED_AUDIT_PATH}`',
    )


def test_historical_route_truth_stays_archived_while_live_docs_stop_claiming_phase_124_closeout() -> None:
    assert_contains_all(
        _MILESTONES_TEXT,
        '## v1.34 Terminal Audit Closure, Contract Hardening & Governance Truth Slimming',
        'historical closeout route truth = `no active milestone route / latest archived baseline = v1.34`',
        'historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.33`',
    )
    assert_contains_all(
        _PROJECT_TEXT,
        '## Latest Archived Milestone (v1.34)',
        'Latest archived pointer',
    )
    assert_not_contains_any(
        _PROJECT_TEXT,
        'Phase 125 planning-ready',
    )
    assert_not_contains_any(
        _ROADMAP_TEXT,
        '**Milestone status:** `active / phase 124 complete; closeout-ready (2026-04-01)`',
        '**Plans**: 0 planned — run `$gsd-execute-phase 125`',
    )
    assert_not_contains_any(
        _STATE_TEXT,
        'Phase 124 complete; closeout-ready for milestone closeout',
        '- **Status:** `active / phase 124 complete; closeout-ready (2026-04-01)`',
    )
