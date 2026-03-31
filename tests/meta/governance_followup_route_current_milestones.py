"""Current active-route and archived-baseline truth guards for v1.31."""

from __future__ import annotations

from .conftest import _as_mapping
from .governance_contract_helpers import _assert_current_route_truth
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_HEADER,
    CURRENT_MILESTONE_ROADMAP_HEADER,
    CURRENT_MILESTONE_STATE_LABEL,
    CURRENT_MILESTONE_STATUS,
    CURRENT_ROUTE_MODE,
    HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH,
    HISTORICAL_CLOSEOUT_ROUTE_TRUTH,
    LATEST_ARCHIVED_AUDIT_PATH,
    LATEST_ARCHIVED_EVIDENCE_PATH,
    LATEST_ARCHIVED_PROJECT_HEADER,
    PREVIOUS_ARCHIVED_PROJECT_HEADER,
    _as_optional_mapping,
    assert_machine_readable_route_contracts,
)
from .governance_followup_route_specs import (
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

_V1_31_TRACES = (
    RequirementTrace("ARC-28", "111"),
    RequirementTrace("GOV-71", "111"),
    RequirementTrace("TST-38", "111"),
    RequirementTrace("ARC-29", "112", "Complete"),
    RequirementTrace("GOV-72", "112", "Complete"),
    RequirementTrace("QLT-46", "113", "Complete"),
    RequirementTrace("OSS-14", "114", "Pending"),
    RequirementTrace("SEC-09", "114", "Pending"),
)


def test_machine_readable_route_contracts_point_to_active_v1_31_and_archived_v1_30() -> None:
    contracts = assert_machine_readable_route_contracts()
    for doc_name in ("PROJECT", "ROADMAP", "REQUIREMENTS", "STATE", "MILESTONES"):
        active = _as_optional_mapping(_as_mapping(contracts[doc_name])["active_milestone"])
        assert active is not None, doc_name
        assert active["version"] == "v1.31"
        assert active["phase"] == "114"

    milestones_contract = _as_mapping(contracts["MILESTONES"])
    latest_archived = _as_mapping(milestones_contract["latest_archived"])
    previous_archived = _as_mapping(milestones_contract["previous_archived"])
    state_bootstrap = _as_mapping(_as_mapping(contracts["STATE"])["bootstrap"])

    assert latest_archived["version"] == "v1.30"
    assert latest_archived["phase"] == "110"
    assert previous_archived["version"] == "v1.29"
    assert state_bootstrap["current_route"] == CURRENT_ROUTE_MODE
    assert state_bootstrap["default_next_command"] == CURRENT_MILESTONE_DEFAULT_NEXT
    assert state_bootstrap["latest_archived_evidence_pointer"] == LATEST_ARCHIVED_EVIDENCE_PATH


def test_phase_113_closeout_and_phase_114_handoff_are_reflected_in_live_docs() -> None:
    _assert_current_route_truth(_PROJECT_TEXT, _ROADMAP_TEXT, _STATE_TEXT)

    assert_contains_all(
        _PROJECT_TEXT,
        CURRENT_MILESTONE_HEADER,
        LATEST_ARCHIVED_PROJECT_HEADER,
        PREVIOUS_ARCHIVED_PROJECT_HEADER,
        f"**Current status:** `{CURRENT_MILESTONE_STATUS}`",
        f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`",
        "Phase 111",
        "Phase 112",
        "Phase 113",
        "Phase 114",
    )
    assert_contains_all(
        _ROADMAP_TEXT,
        CURRENT_MILESTONE_ROADMAP_HEADER,
        f"**Milestone status:** `{CURRENT_MILESTONE_STATUS}`",
        f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`",
        "- [x] **Phase 111: Entity-runtime boundary sealing and dependency-guard hardening**",
        "**Status**: Complete (`2026-03-31`)",
        "**Plans**: 3/3 complete",
        "### Phase 112: Formal-home discoverability and governance-anchor normalization",
    )
    assert_contains_all(
        _STATE_TEXT,
        f"**Current milestone:** `{CURRENT_MILESTONE_STATE_LABEL}`",
        f"**Current mode:** `{CURRENT_ROUTE_MODE}`",
        "- **Phase:** `114 of 114`",
        "- **Status:** `Ready to discuss`",
        "- **Progress:** `[███████░░░] 75%`",
        "## Recommended Next Command",
        "$gsd-discuss-phase 114",
    )


def test_requirements_traceability_advances_phase_111_and_keeps_future_work_pending() -> None:
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_checkbox_markers(*_V1_31_TRACES[:3]),
        *requirement_table_markers(*_V1_31_TRACES),
        "- Current complete: 6",
        "- Current pending: 2",
        f"**Milestone status:** `{CURRENT_MILESTONE_STATUS}`",
        f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`",
    )


def test_historical_route_truth_stays_archived_without_legacy_live_state_wording() -> None:
    assert_contains_all(
        _MILESTONES_TEXT,
        HISTORICAL_CLOSEOUT_ROUTE_TRUTH,
        HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH,
        "## v1.30 Protocol Hotspot Convergence, Transport De-friendization & Snapshot Surface Slimming",
    )
    assert_contains_all(
        _PROJECT_TEXT,
        HISTORICAL_CLOSEOUT_ROUTE_TRUTH,
        HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH,
        LATEST_ARCHIVED_PROJECT_HEADER,
    )
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        HISTORICAL_CLOSEOUT_ROUTE_TRUTH,
        HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH,
        LATEST_ARCHIVED_PROJECT_HEADER,
        LATEST_ARCHIVED_AUDIT_PATH,
    )
    for text in (_MILESTONES_TEXT, _ROADMAP_TEXT, _REQUIREMENTS_TEXT, _PROJECT_TEXT):
        assert_not_contains_any(
            text,
            "current governance state =",
            "当前治理状态已切换为",
            "当前治理状态现已切换为",
            "live governance state",
        )
