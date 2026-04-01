"""Current-route and continuity truth guards for the live selector state."""

from __future__ import annotations

from .governance_contract_helpers import _assert_current_route_truth
from .governance_current_truth import (
    CURRENT_MILESTONE,
    CURRENT_MILESTONE_COMPLETED_PLAN_COUNT,
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_HEADER,
    CURRENT_MILESTONE_PHASES,
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
_PHASE_TERMINAL = CURRENT_MILESTONE_PHASES[-1]


def test_machine_readable_route_contracts_point_to_current_selector_state() -> None:
    contracts = assert_machine_readable_route_contracts()
    for doc_name in ("PROJECT", "ROADMAP", "REQUIREMENTS", "STATE", "MILESTONES"):
        contract = _as_mapping(contracts[doc_name])
        active = _as_optional_mapping(contract["active_milestone"])
        latest_archived = _as_mapping(contract["latest_archived"])
        previous_archived = _as_mapping(contract["previous_archived"])
        bootstrap = _as_mapping(contract["bootstrap"])

        if HAS_ACTIVE_MILESTONE:
            assert active is not None, doc_name
            assert active["version"] == CURRENT_MILESTONE
            assert active["phase"] == CURRENT_PHASE
            assert active["status"] == CURRENT_MILESTONE_STATUS
        else:
            assert active is None, doc_name
            assert latest_archived["version"] == CURRENT_MILESTONE
            assert latest_archived["phase"] == CURRENT_PHASE
            assert latest_archived["status"] == CURRENT_MILESTONE_STATUS
        assert latest_archived["version"] == LATEST_ARCHIVED_MILESTONE
        assert previous_archived["version"] == "v1.35"
        assert bootstrap["current_route"] == CURRENT_ROUTE_MODE
        assert bootstrap["default_next_command"] == CURRENT_MILESTONE_DEFAULT_NEXT
        assert bootstrap["latest_archived_evidence_pointer"] == LATEST_ARCHIVED_EVIDENCE_PATH


def test_current_truth_is_reflected_in_live_docs() -> None:
    _assert_current_route_truth(_PROJECT_TEXT, _ROADMAP_TEXT, _STATE_TEXT)

    assert_contains_all(
        _PROJECT_TEXT,
        CURRENT_MILESTONE_HEADER,
        PREVIOUS_ARCHIVED_PROJECT_HEADER,
        f"**Current status:** `{CURRENT_MILESTONE_STATUS}`",
        f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`",
    )
    if HAS_ACTIVE_MILESTONE:
        assert_contains_all(
            _ROADMAP_TEXT,
            CURRENT_MILESTONE_ROADMAP_HEADER,
            f"**Milestone status:** `{CURRENT_MILESTONE_STATUS}`",
            f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`",
            CURRENT_PHASE_HEADING,
            "## Phases",
            "## Progress",
        )
        for phase in CURRENT_MILESTONE_PHASES:
            assert f"Phase {phase}" in _ROADMAP_TEXT
        assert_contains_all(
            _STATE_TEXT,
            f"**Current milestone:** `{CURRENT_MILESTONE_STATE_LABEL}`",
            f"**Current mode:** `{CURRENT_ROUTE_MODE}`",
            f"- **Phase:** `{CURRENT_PHASE} of {_PHASE_TERMINAL}`",
            f"- **Plan:** `{CURRENT_MILESTONE_COMPLETED_PLAN_COUNT} of {CURRENT_MILESTONE_TOTAL_PLAN_COUNT}`",
            f"- **Status:** `{CURRENT_MILESTONE_STATUS}`",
            "## Recommended Next Command",
            CURRENT_MILESTONE_DEFAULT_NEXT,
            "active milestone route",
        )
    else:
        assert_contains_all(
            _ROADMAP_TEXT,
            CURRENT_MILESTONE_ROADMAP_HEADER,
            f"**Milestone status:** `{CURRENT_MILESTONE_STATUS}`",
            f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`",
            "## Phases",
            "## Progress",
            "Latest Archived Milestone",
        )
        assert_contains_all(
            _STATE_TEXT,
            f"**Current milestone:** `{CURRENT_MILESTONE_STATE_LABEL}`",
            f"**Current mode:** `{CURRENT_ROUTE_MODE}`",
            f"- **Phase:** `{CURRENT_PHASE} of {CURRENT_PHASE}`",
            f"- **Plan:** `{CURRENT_MILESTONE_COMPLETED_PLAN_COUNT} of {CURRENT_MILESTONE_TOTAL_PLAN_COUNT}`",
            f"- **Status:** `{CURRENT_MILESTONE_STATUS}`",
            "## Recommended Next Command",
            CURRENT_MILESTONE_DEFAULT_NEXT,
            "No active milestone route",
        )


def test_current_requirements_traceability_and_coverage_stay_in_sync() -> None:
    base_markers = (
        f"**Milestone status:** `{CURRENT_MILESTONE_STATUS}`",
        f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`",
        f"**Latest archived baseline:** `{LATEST_ARCHIVED_MILESTONE}`",
        f"**Archive pointer:** `{LATEST_ARCHIVED_EVIDENCE_PATH}`",
        f"**Latest archived audit artifact:** `{LATEST_ARCHIVED_AUDIT_PATH}`",
    )
    assert_contains_all(_REQUIREMENTS_TEXT, *base_markers)

    if CURRENT_MILESTONE == "v1.37":
        assert_contains_all(
            _REQUIREMENTS_TEXT,
            "- [x] **ARC-40**",
            "- [x] **HOT-59**",
            "- [x] **TST-50**",
            "- [x] **QLT-52**",
            "| ARC-40 | Phase 129 | Complete |",
            "| HOT-59 | Phase 129 | Complete |",
            "| TST-50 | Phase 129 | Complete |",
            "| QLT-52 | Phase 129 | Complete |",
            "- v1.37 requirements: 12 total",
            "- Mapped to phases: 12",
            "- Complete: 4",
            "- Pending: 8",
        )
        return

    assert_contains_all(
        _REQUIREMENTS_TEXT,
        "- [x] **ARC-38**",
        "- [x] **HOT-57**",
        "- [x] **GOV-85**",
        "- [x] **TST-48**",
        "- [x] **QLT-50**",
        "- [x] **DOC-15**",
        "- [x] **ARC-39**",
        "- [x] **HOT-58**",
        "- [x] **TST-49**",
        "- [x] **OSS-17**",
        "- [x] **GOV-86**",
        "- [x] **QLT-51**",
        "| OSS-17 | Phase 128 | Complete |",
        "| GOV-86 | Phase 128 | Complete |",
        "| QLT-51 | Phase 128 | Complete |",
        "- v1.36 requirements: 12 total",
        "- Mapped to phases: 12",
        "- Complete: 12",
        "- Pending: 0",
    )


def test_historical_route_truth_stays_archived_while_live_docs_stop_claiming_old_handoffs() -> None:
    assert_contains_all(
        _MILESTONES_TEXT,
        "## Previous Archived Milestone (v1.35)",
        "historical closeout route truth = `no active milestone route / latest archived baseline = v1.35`",
        "historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.34`",
    )
    assert_contains_all(_PROJECT_TEXT, "## Previous Archived Milestone (v1.35)", "Latest archived pointer")
    assert_not_contains_any(
        _PROJECT_TEXT,
        "Phase 125 planning-ready",
        "Phase 127 complete; phase 128 planning-ready",
    )
    assert_not_contains_any(
        _ROADMAP_TEXT,
        "**Milestone status:** `active / phase 124 complete; closeout-ready (2026-04-01)`",
        "**Milestone status:** `active / phase 127 complete; phase 128 planning-ready (2026-04-01)`",
        "**Plans**: 0 planned — run `$gsd-execute-phase 125`",
    )
    assert_not_contains_any(
        _STATE_TEXT,
        "Phase 124 complete; closeout-ready for milestone closeout",
        "Phase 127 complete; next step = $gsd-plan-phase 128",
        "- **Status:** `active / phase 124 complete; closeout-ready (2026-04-01)`",
    )
