"""Current-milestone and continuity truth guards for the active v1.34 Phase 120 route."""

from __future__ import annotations

from .governance_contract_helpers import _assert_current_route_truth
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_HEADER,
    CURRENT_MILESTONE_ROADMAP_HEADER,
    CURRENT_MILESTONE_STATE_LABEL,
    CURRENT_MILESTONE_STATUS,
    CURRENT_PHASE,
    CURRENT_PHASE_HEADING,
    CURRENT_ROUTE_MODE,
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
    RequirementTrace,
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

_V1_34_TRACES = (
    RequirementTrace('ARC-32', '120'),
    RequirementTrace('HOT-52', '120'),
    RequirementTrace('QLT-47', '120'),
    RequirementTrace('GOV-78', '120'),
    RequirementTrace('GOV-79', '120'),
    RequirementTrace('DOC-10', '120'),
    RequirementTrace('OSS-15', '120'),
    RequirementTrace('TST-42', '120'),
)


def test_machine_readable_route_contracts_point_to_active_v1_34_phase_120_route() -> None:
    contracts = assert_machine_readable_route_contracts()
    for doc_name in ('PROJECT', 'ROADMAP', 'REQUIREMENTS', 'STATE', 'MILESTONES'):
        contract = _as_mapping(contracts[doc_name])
        active = _as_optional_mapping(contract['active_milestone'])
        latest_archived = _as_mapping(contract['latest_archived'])
        previous_archived = _as_mapping(contract['previous_archived'])
        bootstrap = _as_mapping(contract['bootstrap'])

        assert active is not None, doc_name
        assert active['version'] == 'v1.34'
        assert active['phase'] == '120'
        assert active['status'] == 'active / phase 120 complete; closeout-ready (2026-04-01)'
        assert latest_archived['version'] == 'v1.33'
        assert latest_archived['phase'] == '119'
        assert latest_archived['status'] == 'archived / evidence-ready (2026-04-01)'
        assert previous_archived['version'] == 'v1.32'
        assert bootstrap['current_route'] == CURRENT_ROUTE_MODE
        assert bootstrap['default_next_command'] == CURRENT_MILESTONE_DEFAULT_NEXT
        assert bootstrap['latest_archived_evidence_pointer'] == LATEST_ARCHIVED_EVIDENCE_PATH


def test_active_v1_34_truth_is_reflected_in_live_docs() -> None:
    _assert_current_route_truth(_PROJECT_TEXT, _ROADMAP_TEXT, _STATE_TEXT)

    assert_contains_all(
        _PROJECT_TEXT,
        CURRENT_MILESTONE_HEADER,
        LATEST_ARCHIVED_PROJECT_HEADER,
        PREVIOUS_ARCHIVED_PROJECT_HEADER,
        f'**Current status:** `{CURRENT_MILESTONE_STATUS}`',
        f'**Default next step:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`',
        'Phase 120',
        'stable pointer',
    )
    assert_contains_all(
        _ROADMAP_TEXT,
        CURRENT_MILESTONE_ROADMAP_HEADER,
        CURRENT_PHASE_HEADING,
        f'**Milestone status:** `{CURRENT_MILESTONE_STATUS}`',
        f'**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`',
        'Phase 120: terminal audit closure, contract hardening, and governance truth slimming',
        '`120-01` runtime/service contract tightening and runtime-access normalization',
        '`120-02` flow error taxonomy hardening and single-source send-command validation',
        '`120-03` toolchain guard de-brittling, docs appendix slimming, and stable governance pointers',
    )
    assert_contains_all(
        _STATE_TEXT,
        f'**Current milestone:** `{CURRENT_MILESTONE_STATE_LABEL}`',
        f'**Current mode:** `{CURRENT_ROUTE_MODE}`',
        f'- **Phase:** `{CURRENT_PHASE} of {CURRENT_PHASE}`',
        f'- **Status:** `{CURRENT_MILESTONE_STATUS}`',
        '## Recommended Next Command',
        CURRENT_MILESTONE_DEFAULT_NEXT,
        '120-01 .. 120-03',
    )
    assert '- **Plan:** `3 of 3`' in _STATE_TEXT


def test_v1_34_requirements_traceability_and_coverage_are_phase_120_complete() -> None:
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
        '| ARC-32 | Phase 120 | Complete |',
        '| HOT-52 | Phase 120 | Complete |',
        '| QLT-47 | Phase 120 | Complete |',
        '| GOV-78 | Phase 120 | Complete |',
        '| GOV-79 | Phase 120 | Complete |',
        '| DOC-10 | Phase 120 | Complete |',
        '| OSS-15 | Phase 120 | Complete |',
        '| TST-42 | Phase 120 | Complete |',
        '- v1.34 requirements: 8 total',
        '- Mapped to phases: 8',
        '- Complete: 8',
        '- Pending: 0',
        f'**Milestone status:** `{CURRENT_MILESTONE_STATUS}`',
        f'**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`',
        f'**Latest archived baseline:** `{LATEST_ARCHIVED_MILESTONE}`',
        f'**Archive pointer:** `{LATEST_ARCHIVED_EVIDENCE_PATH}`',
        f'**Latest archived audit artifact:** `{LATEST_ARCHIVED_AUDIT_PATH}`',
    )


def test_historical_route_truth_stays_archived_while_live_docs_stop_claiming_v1_33_is_current() -> None:
    assert_contains_all(
        _MILESTONES_TEXT,
        '## Latest Archived Milestone (v1.33)',
        'historical closeout route truth = `no active milestone route / latest archived baseline = v1.33`',
        'historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.32`',
    )
    assert_contains_all(
        _PROJECT_TEXT,
        '## Latest Archived Milestone (v1.33)',
        'Latest archived pointer',
    )
    assert_not_contains_any(
        _PROJECT_TEXT,
        '**Default next step:** `$gsd-plan-phase 120`',
        '**Current route:** `no active milestone route / latest archived baseline = v1.33`',
    )
    assert_not_contains_any(
        _ROADMAP_TEXT,
        'default next = `$gsd-plan-phase 120`',
        '**Milestone status:** `active / planning-ready (2026-04-01)`',
    )
    assert_not_contains_any(
        _STATE_TEXT,
        'Phase 120 pending planning',
        '- **Status:** `active / planning-ready (2026-04-01)`',
    )
