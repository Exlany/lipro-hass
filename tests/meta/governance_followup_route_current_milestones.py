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
    PREVIOUS_ARCHIVED_MILESTONE,
    PREVIOUS_ARCHIVED_PROJECT_HEADER,
    _as_mapping,
    _as_optional_mapping,
    assert_machine_readable_route_contracts,
)
from .governance_followup_route_specs import (
    CoverageSnapshot,
    RequirementTrace,
    assert_contains_all,
    assert_not_contains_any,
    load_planning_docs_snapshot,
    requirement_checkbox_markers,
    requirement_table_markers,
)

_SNAPSHOT = load_planning_docs_snapshot()
_MILESTONES_TEXT = _SNAPSHOT.milestones
_ROADMAP_TEXT = _SNAPSHOT.roadmap
_REQUIREMENTS_TEXT = _SNAPSHOT.requirements
_PROJECT_TEXT = _SNAPSHOT.project
_STATE_TEXT = _SNAPSHOT.state
_PHASE_TERMINAL = CURRENT_MILESTONE_PHASES[-1]

_REQUIREMENT_TRACES_BY_MILESTONE = {
    "v1.41": (
        RequirementTrace("AUD-08", "136"),
        RequirementTrace("GOV-91", "136"),
        RequirementTrace("DOC-19", "136"),
        RequirementTrace("ARC-45", "136"),
        RequirementTrace("QLT-58", "136"),
        RequirementTrace("TST-56", "136"),
    ),
    "v1.40": (
        RequirementTrace("GOV-90", "134"),
        RequirementTrace("ARC-43", "134"),
        RequirementTrace("HOT-62", "134"),
        RequirementTrace("HOT-63", "134"),
        RequirementTrace("QLT-56", "134"),
        RequirementTrace("TST-54", "134"),
        RequirementTrace("ARC-44", "135"),
        RequirementTrace("HOT-64", "135"),
        RequirementTrace("HOT-65", "135"),
        RequirementTrace("HOT-66", "135"),
        RequirementTrace("QLT-57", "135"),
        RequirementTrace("TST-55", "135"),
    ),
    "v1.39": (
        RequirementTrace("GOV-89", "133"),
        RequirementTrace("ARC-42", "133"),
        RequirementTrace("HOT-61", "133"),
        RequirementTrace("DOC-18", "133"),
        RequirementTrace("QLT-55", "133"),
        RequirementTrace("TST-53", "133"),
    ),
    "v1.38": (
        RequirementTrace("AUD-07", "132"),
        RequirementTrace("GOV-88", "132"),
        RequirementTrace("DOC-17", "132"),
        RequirementTrace("OSS-19", "132"),
        RequirementTrace("QLT-54", "132"),
        RequirementTrace("TST-52", "132"),
    ),
    "v1.37": (
        RequirementTrace("AUD-06", "131"),
        RequirementTrace("GOV-87", "131"),
        RequirementTrace("DOC-16", "131"),
        RequirementTrace("OSS-18", "131"),
        RequirementTrace("ARC-40", "129"),
        RequirementTrace("HOT-59", "129"),
        RequirementTrace("TST-50", "129"),
        RequirementTrace("QLT-52", "129"),
        RequirementTrace("ARC-41", "130"),
        RequirementTrace("HOT-60", "130"),
        RequirementTrace("TST-51", "130"),
        RequirementTrace("QLT-53", "131"),
    ),
}

_COVERAGE_BY_MILESTONE = {
    "v1.41": CoverageSnapshot("v1.41 requirements", 6, mapped=6, complete=6, pending=0),
    "v1.40": CoverageSnapshot("v1.40 requirements", 12, mapped=12, complete=12, pending=0),
    "v1.39": CoverageSnapshot("v1.39 requirements", 6, mapped=6, complete=6, pending=0),
    "v1.38": CoverageSnapshot("v1.38 requirements", 6, mapped=6, complete=6, pending=0),
    "v1.37": CoverageSnapshot(
        "v1.37 requirements", 12, mapped=12, complete=12, pending=0
    ),
}


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
        assert previous_archived["version"] == PREVIOUS_ARCHIVED_MILESTONE
        assert bootstrap["current_route"] == CURRENT_ROUTE_MODE
        assert bootstrap["default_next_command"] == CURRENT_MILESTONE_DEFAULT_NEXT
        assert (
            bootstrap["latest_archived_evidence_pointer"]
            == LATEST_ARCHIVED_EVIDENCE_PATH
        )


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

    traces = _REQUIREMENT_TRACES_BY_MILESTONE.get(CURRENT_MILESTONE)
    coverage = _COVERAGE_BY_MILESTONE.get(CURRENT_MILESTONE)

    assert traces is not None, CURRENT_MILESTONE
    assert coverage is not None, CURRENT_MILESTONE

    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_checkbox_markers(*traces),
        *requirement_table_markers(*traces),
        *coverage.markers(),
    )


def test_historical_route_truth_stays_archived_while_live_docs_stop_claiming_old_handoffs() -> (
    None
):
    previous_minor = int(PREVIOUS_ARCHIVED_MILESTONE.split(".")[-1])
    expected_closeout = (
        "historical closeout route truth = "
        f"`no active milestone route / latest archived baseline = {PREVIOUS_ARCHIVED_MILESTONE}`"
    )
    expected_transition = (
        "historical archive-transition route truth = "
        f"`no active milestone route / latest archived baseline = v1.{previous_minor - 1}`"
    )
    assert_contains_all(
        _MILESTONES_TEXT,
        PREVIOUS_ARCHIVED_PROJECT_HEADER,
        expected_closeout,
        expected_transition,
    )
    assert_contains_all(
        _PROJECT_TEXT, PREVIOUS_ARCHIVED_PROJECT_HEADER, "Latest archived pointer"
    )
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
