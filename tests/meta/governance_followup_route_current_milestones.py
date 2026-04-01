"""Current-milestone and continuity truth guards for the archived v1.34 baseline."""

from __future__ import annotations

from .governance_contract_helpers import _assert_current_route_truth
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_HEADER,
    CURRENT_MILESTONE_ROADMAP_HEADER,
    CURRENT_MILESTONE_STATE_LABEL,
    CURRENT_MILESTONE_STATUS,
    CURRENT_ROUTE_MODE,
    HAS_ACTIVE_MILESTONE,
    LATEST_ARCHIVED_AUDIT_PATH,
    LATEST_ARCHIVED_EVIDENCE_PATH,
    LATEST_ARCHIVED_MILESTONE,
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


def test_machine_readable_route_contracts_point_to_archived_v1_34_latest_baseline() -> None:
    contracts = assert_machine_readable_route_contracts()
    for doc_name in ('PROJECT', 'ROADMAP', 'REQUIREMENTS', 'STATE', 'MILESTONES'):
        contract = _as_mapping(contracts[doc_name])
        active = _as_optional_mapping(contract['active_milestone'])
        latest_archived = _as_mapping(contract['latest_archived'])
        previous_archived = _as_mapping(contract['previous_archived'])
        bootstrap = _as_mapping(contract['bootstrap'])

        assert active is None, doc_name
        assert latest_archived['version'] == 'v1.34'
        assert latest_archived['phase'] == '121'
        assert latest_archived['status'] == 'archived / evidence-ready (2026-04-01)'
        assert previous_archived['version'] == 'v1.33'
        assert bootstrap['current_route'] == CURRENT_ROUTE_MODE
        assert bootstrap['default_next_command'] == CURRENT_MILESTONE_DEFAULT_NEXT
        assert bootstrap['latest_archived_evidence_pointer'] == LATEST_ARCHIVED_EVIDENCE_PATH


def test_archived_v1_34_truth_is_reflected_in_live_docs() -> None:
    _assert_current_route_truth(_PROJECT_TEXT, _ROADMAP_TEXT, _STATE_TEXT)

    assert HAS_ACTIVE_MILESTONE is False
    assert_contains_all(
        _PROJECT_TEXT,
        CURRENT_MILESTONE_HEADER,
        PREVIOUS_ARCHIVED_PROJECT_HEADER,
        f'**Current status:** `{CURRENT_MILESTONE_STATUS}`',
        f'**Default next step:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`',
        'raw coordinator',
        'phase-labeled live owner',
    )
    assert_contains_all(
        _ROADMAP_TEXT,
        CURRENT_MILESTONE_ROADMAP_HEADER,
        f'**Milestone status:** `{CURRENT_MILESTONE_STATUS}`',
        f'**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`',
        'Phase 120: terminal audit closure, contract hardening, and governance truth slimming',
        'Phase 121: residual contract closure, flow invariant tightening, and surface hygiene cleanup',
        '## Archived Highlights',
        '## Progress',
    )
    assert_contains_all(
        _STATE_TEXT,
        f'**Current milestone:** `{CURRENT_MILESTONE_STATE_LABEL}`',
        f'**Current mode:** `{CURRENT_ROUTE_MODE}`',
        '- **Phase:** `121 of 121`',
        '- **Plan:** `6 of 6`',
        f'- **Status:** `{CURRENT_MILESTONE_STATUS}`',
        '## Recommended Next Command',
        CURRENT_MILESTONE_DEFAULT_NEXT,
        'archive promotion',
    )


def test_v1_34_requirements_traceability_and_coverage_are_archived_complete() -> None:
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        '- [x] **ARC-32**',
        '- [x] **HOT-52**',
        '- [x] **QLT-47**',
        '- [x] **GOV-78**',
        '- [x] **GOV-79**',
        '- [x] **DOC-10**',
        '- [x] **OSS-15**',
        '- [x] **TST-42**',
        '- [x] **ARC-33**',
        '- [x] **QLT-48**',
        '- [x] **HOT-53**',
        '- [x] **GOV-80**',
        '- [x] **DOC-11**',
        '- [x] **TST-43**',
        '| ARC-32 | Phase 120 | Complete |',
        '| HOT-52 | Phase 120 | Complete |',
        '| QLT-47 | Phase 120 | Complete |',
        '| GOV-78 | Phase 120 | Complete |',
        '| GOV-79 | Phase 120 | Complete |',
        '| DOC-10 | Phase 120 | Complete |',
        '| OSS-15 | Phase 120 | Complete |',
        '| TST-42 | Phase 120 | Complete |',
        '| ARC-33 | Phase 121 | Complete |',
        '| QLT-48 | Phase 121 | Complete |',
        '| HOT-53 | Phase 121 | Complete |',
        '| GOV-80 | Phase 121 | Complete |',
        '| DOC-11 | Phase 121 | Complete |',
        '| TST-43 | Phase 121 | Complete |',
        '- v1.34 requirements: 14 total',
        '- Mapped to phases: 14',
        '- Complete: 14',
        '- Pending: 0',
        f'**Milestone status:** `{CURRENT_MILESTONE_STATUS}`',
        f'**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`',
        f'**Latest archived baseline:** `{LATEST_ARCHIVED_MILESTONE}`',
        f'**Archive pointer:** `{LATEST_ARCHIVED_EVIDENCE_PATH}`',
        f'**Current audit artifact:** `{LATEST_ARCHIVED_AUDIT_PATH}`',
    )


def test_historical_route_truth_stays_archived_while_live_docs_stop_claiming_v1_33_is_current() -> None:
    assert_contains_all(
        _MILESTONES_TEXT,
        '## Previous Archived Milestone (v1.33)',
        'historical closeout route truth = `no active milestone route / latest archived baseline = v1.33`',
        'historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.32`',
    )
    assert_contains_all(
        _PROJECT_TEXT,
        '## Previous Archived Milestone (v1.33)',
        'Latest archived pointer',
    )
    assert_not_contains_any(
        _PROJECT_TEXT,
        '**Default next step:** `$gsd-complete-milestone v1.34`',
        '**Current route:** `v1.34 active milestone route / starting from latest archived baseline = v1.33`',
    )
    assert_not_contains_any(
        _ROADMAP_TEXT,
        'default next = `$gsd-complete-milestone v1.34`',
        '**Milestone status:** `active / phase 121 complete; closeout-ready (2026-04-01)`',
    )
    assert_not_contains_any(
        _STATE_TEXT,
        'Phase 121 complete; closeout-ready for milestone closeout',
        '- **Status:** `active / phase 121 complete; closeout-ready (2026-04-01)`',
    )
