"""Current-milestone and continuity truth guards for the active v1.33 route."""

from __future__ import annotations

from .conftest import _as_mapping
from .governance_contract_helpers import _assert_current_route_truth
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_HEADER,
    CURRENT_MILESTONE_ROADMAP_HEADER,
    CURRENT_MILESTONE_STATE_LABEL,
    CURRENT_MILESTONE_STATUS,
    CURRENT_PHASE,
    CURRENT_PHASE_HEADING,
    CURRENT_PHASE_PLAN_FILENAMES,
    CURRENT_PHASE_SUMMARY_FILENAMES,
    CURRENT_PHASE_VERIFICATION_FILENAME,
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

_V1_33_TRACES = (
    RequirementTrace("ARC-30", "119"),
    RequirementTrace("ARC-31", "119"),
    RequirementTrace("GOV-76", "119"),
    RequirementTrace("GOV-77", "119"),
    RequirementTrace("TST-41", "119"),
)


def test_machine_readable_route_contracts_point_to_active_v1_33_closeout_ready_route() -> None:
    contracts = assert_machine_readable_route_contracts()
    for doc_name in ("PROJECT", "ROADMAP", "REQUIREMENTS", "STATE", "MILESTONES"):
        contract = _as_mapping(contracts[doc_name])
        active = _as_optional_mapping(contract["active_milestone"])
        latest_archived = _as_mapping(contract["latest_archived"])
        previous_archived = _as_mapping(contract["previous_archived"])
        bootstrap = _as_mapping(contract["bootstrap"])

        assert active is not None, doc_name
        assert active["version"] == "v1.33"
        assert active["phase"] == "119"
        assert active["status"] == "active / phase 119 complete; closeout-ready (2026-04-01)"
        assert latest_archived["version"] == "v1.32"
        assert previous_archived["version"] == "v1.31"
        assert bootstrap["current_route"] == CURRENT_ROUTE_MODE
        assert bootstrap["default_next_command"] == CURRENT_MILESTONE_DEFAULT_NEXT
        assert bootstrap["latest_archived_evidence_pointer"] == LATEST_ARCHIVED_EVIDENCE_PATH


def test_active_v1_33_truth_is_reflected_in_live_docs() -> None:
    _assert_current_route_truth(_PROJECT_TEXT, _ROADMAP_TEXT, _STATE_TEXT)

    assert_contains_all(
        _PROJECT_TEXT,
        CURRENT_MILESTONE_HEADER,
        PREVIOUS_ARCHIVED_PROJECT_HEADER,
        f"**Current status:** `{CURRENT_MILESTONE_STATUS}`",
        f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`",
        "Phase 119",
    )
    assert_contains_all(
        _ROADMAP_TEXT,
        CURRENT_MILESTONE_ROADMAP_HEADER,
        CURRENT_PHASE_HEADING,
        f"**Milestone status:** `{CURRENT_MILESTONE_STATUS}`",
        f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`",
        "**Status**: Complete (`2026-04-01`)",
        "**Plans**: 3/3 complete",
        *CURRENT_PHASE_PLAN_FILENAMES,
        *CURRENT_PHASE_SUMMARY_FILENAMES,
        CURRENT_PHASE_VERIFICATION_FILENAME,
        "**Closeout proof**: `119-01` 已交付 MQTT boundary 单向 authority 与 focused guard 冻结；`119-02` 已交付 runtime/service contract single-source truth；`119-03` 已交付 semver-only release namespace、canonical governance route helper 与 docs/changelog freshness 收口。",
    )
    assert_contains_all(
        _STATE_TEXT,
        f"**Current milestone:** `{CURRENT_MILESTONE_STATE_LABEL}`",
        f"**Current mode:** `{CURRENT_ROUTE_MODE}`",
        f"- **Phase:** `{CURRENT_PHASE} of {CURRENT_PHASE}`",
        "- **Plan:** `3 of 3`",
        f"- **Status:** `{CURRENT_MILESTONE_STATUS}`",
        "- **Progress:** `[██████████] 100%`",
        "## Recommended Next Command",
        "$gsd-complete-milestone v1.33",
    )


def test_v1_33_requirements_traceability_and_coverage_are_complete() -> None:
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_checkbox_markers(*_V1_33_TRACES),
        *requirement_table_markers(*_V1_33_TRACES),
        "- [x] **ARC-30**",
        "- [x] **ARC-31**",
        "- [x] **GOV-76**",
        "- [x] **GOV-77**",
        "- [x] **TST-41**",
        "| ARC-30 | Phase 119 | Complete |",
        "| ARC-31 | Phase 119 | Complete |",
        "| GOV-76 | Phase 119 | Complete |",
        "| GOV-77 | Phase 119 | Complete |",
        "| TST-41 | Phase 119 | Complete |",
        "- v1.33 requirements: 5 total",
        "- Mapped to phases: 5",
        "- Complete: 5",
        "- Pending: 0",
        f"**Milestone status:** `{CURRENT_MILESTONE_STATUS}`",
        f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`",
        "**Latest archived baseline:** `v1.32`",
        "**Archive pointer:** `.planning/reviews/V1_32_EVIDENCE_INDEX.md`",
        "**Starting audit artifact:** `.planning/v1.32-MILESTONE-AUDIT.md`",
    )


def test_historical_route_truth_stays_archived_without_stale_phase_119_planning_wording() -> None:
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
        PREVIOUS_ARCHIVED_PROJECT_HEADER,
    )
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        HISTORICAL_CLOSEOUT_ROUTE_TRUTH,
        HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH,
        LATEST_ARCHIVED_PROJECT_HEADER,
        LATEST_ARCHIVED_AUDIT_PATH,
    )
    for text in (_MILESTONES_TEXT, _ROADMAP_TEXT, _REQUIREMENTS_TEXT, _PROJECT_TEXT, _STATE_TEXT):
        assert_not_contains_any(
            text,
            "current governance state =",
            "当前治理状态已切换为",
            "当前治理状态现已切换为",
            "live governance state",
            "$gsd-plan-phase 119",
            "planning pending 2026-04-01",
            "Phase 119 planning pending",
            "active / roadmap drafted; phase 119 pending planning (2026-04-01)",
            "$gsd-execute-phase 119",
        )
