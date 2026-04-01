"""Active-route and continuity truth guards for the current v1.32 milestone."""

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

_V1_32_TRACES = (
    RequirementTrace("HOT-48", "115"),
    RequirementTrace("HOT-49", "116"),
    RequirementTrace("TST-39", "117"),
    RequirementTrace("GOV-73", "117"),
    RequirementTrace("GOV-75", "118"),
)


def test_machine_readable_route_contracts_point_to_active_v1_32_phase118_execution_ready() -> None:
    contracts = assert_machine_readable_route_contracts()
    for doc_name in ("PROJECT", "ROADMAP", "REQUIREMENTS", "STATE", "MILESTONES"):
        active = _as_optional_mapping(_as_mapping(contracts[doc_name])["active_milestone"])
        assert active is not None, doc_name
        assert active["version"] == "v1.32"
        assert active["phase"] == "118"
        assert active["status"] == "active / phase 118 execution-ready (2026-04-01)"

    milestones_contract = _as_mapping(contracts["MILESTONES"])
    latest_archived = _as_mapping(milestones_contract["latest_archived"])
    previous_archived = _as_mapping(milestones_contract["previous_archived"])
    state_bootstrap = _as_mapping(_as_mapping(contracts["STATE"])["bootstrap"])

    assert latest_archived["version"] == "v1.31"
    assert latest_archived["phase"] == "114"
    assert previous_archived["version"] == "v1.30"
    assert state_bootstrap["current_route"] == CURRENT_ROUTE_MODE
    assert state_bootstrap["default_next_command"] == CURRENT_MILESTONE_DEFAULT_NEXT
    assert state_bootstrap["latest_archived_evidence_pointer"] == LATEST_ARCHIVED_EVIDENCE_PATH


def test_active_v1_32_truth_is_reflected_in_live_docs() -> None:
    _assert_current_route_truth(_PROJECT_TEXT, _ROADMAP_TEXT, _STATE_TEXT)

    assert_contains_all(
        _PROJECT_TEXT,
        CURRENT_MILESTONE_HEADER,
        LATEST_ARCHIVED_PROJECT_HEADER,
        PREVIOUS_ARCHIVED_PROJECT_HEADER,
        f"**Current status:** `{CURRENT_MILESTONE_STATUS}`",
        f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`",
        "Phase 115",
        "Phase 116",
        "Phase 117",
        "Phase 118",
    )
    assert_contains_all(
        _ROADMAP_TEXT,
        CURRENT_MILESTONE_ROADMAP_HEADER,
        f"**Milestone status:** `{CURRENT_MILESTONE_STATUS}`",
        f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`",
        "### Phase 115: Status-fallback query-flow normalization",
        "### Phase 116: Anonymous-share and REST façade hotspot slimming",
        "### Phase 117: Validation backfill and continuity hardening",
        "### Phase 118: Final hotspot decomposition and validation closure",
        "**Status**: Execution-ready (`2026-04-01`)",
        "**Plans**: 1/3 complete",
        "118-01-PLAN.md",
        "118-01-SUMMARY.md",
        "**Current activation proof**: `118-01` 已交付 `GOV-75` route truth sync；remaining execution queue = `118-02` hotspot decomposition + `118-03` validation closure.",
    )
    assert_contains_all(
        _STATE_TEXT,
        f"**Current milestone:** `{CURRENT_MILESTONE_STATE_LABEL}`",
        f"**Current mode:** `{CURRENT_ROUTE_MODE}`",
        "- **Phase:** `118 of 118`",
        "- **Plan:** `1 of 3`",
        f"- **Status:** `{CURRENT_MILESTONE_STATUS}`",
        "- **Progress:** `[████████░░] 80%`",
        "## Recommended Next Command",
        "$gsd-execute-phase 118",
    )


def test_v1_32_requirements_traceability_and_coverage_are_complete() -> None:
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_checkbox_markers(*_V1_32_TRACES),
        *requirement_table_markers(*_V1_32_TRACES),
        "- [ ] **HOT-50**",
        "- [ ] **HOT-51**",
        "- [ ] **TST-40**",
        "| HOT-50 | Phase 118 | Pending |",
        "| HOT-51 | Phase 118 | Pending |",
        "| TST-40 | Phase 118 | Pending |",
        "- v1.32 requirements: 8 total",
        "- Mapped to phases: 8",
        "- Complete: 5",
        "- Pending: 3",
        f"**Milestone status:** `{CURRENT_MILESTONE_STATUS}`",
        f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`",
        "**Latest archived baseline:** `v1.31`",
    )


def test_historical_route_truth_stays_archived_without_stale_phase117_handoff_wording() -> None:
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
            "active / phase 116 complete; phase 117 discuss-ready (2026-03-31)",
            "$gsd-discuss-phase 117",
            "$gsd-execute-phase 117",
            "Phase 117 execution-ready",
        )
