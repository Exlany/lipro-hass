"""Current-route and archived-baseline follow-up truth guards spanning v1.8-v1.30."""

from __future__ import annotations

from .conftest import _as_mapping
from .governance_contract_helpers import _assert_current_route_truth
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_HEADER,
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
    CoverageSnapshot,
    RequirementTrace,
    assert_contains_all,
    assert_not_contains_any,
    load_planning_docs_snapshot,
    requirement_checkbox_markers,
    requirement_table_markers,
)
from .governance_promoted_assets import _assert_promoted_closeout_package

_SNAPSHOT = load_planning_docs_snapshot()
_MILESTONES_TEXT = _SNAPSHOT.milestones
_ROADMAP_TEXT = _SNAPSHOT.roadmap
_REQUIREMENTS_TEXT = _SNAPSHOT.requirements
_PROJECT_TEXT = _SNAPSHOT.project
_STATE_TEXT = _SNAPSHOT.state

_V1_8_TRACES = (
    RequirementTrace("GOV-38", "51"),
    RequirementTrace("GOV-39", "52"),
    RequirementTrace("QLT-18", "53"),
    RequirementTrace("ARC-08", "53"),
    RequirementTrace("HOT-12", "54"),
    RequirementTrace("HOT-13", "54"),
    RequirementTrace("TST-10", "55"),
    RequirementTrace("TYP-13", "55"),
)
_V1_9_TRACES = (
    RequirementTrace("RES-13", "56"),
    RequirementTrace("ARC-09", "56"),
    RequirementTrace("GOV-40", "56"),
)
_V1_10_TRACES = (
    RequirementTrace("ERR-12", "57"),
    RequirementTrace("TYP-14", "57"),
    RequirementTrace("GOV-41", "57"),
)
_V1_11_TRACES = (
    RequirementTrace("AUD-03", "58"),
    RequirementTrace("ARC-10", "58"),
    RequirementTrace("OSS-06", "58"),
    RequirementTrace("GOV-42", "58"),
)
_V1_12_TRACES = (
    RequirementTrace("TST-11", "59"),
    RequirementTrace("QLT-19", "59"),
    RequirementTrace("GOV-43", "59"),
)
_V1_13_TRACES = (
    RequirementTrace("HOT-14", "60"),
    RequirementTrace("TST-12", "60"),
    RequirementTrace("GOV-44", "60"),
)

_V1_30_TRACES = (
    RequirementTrace("HOT-46", "107"),
    RequirementTrace("ARC-27", "107"),
    RequirementTrace("TST-37", "107"),
    RequirementTrace("QLT-45", "107"),
    RequirementTrace("RUN-10", "108"),
    RequirementTrace("HOT-47", "109", "Planned"),
    RequirementTrace("RUN-11", "110", "Planned"),
    RequirementTrace("GOV-70", "110", "Planned"),
)

_V1_8_COVERAGE = CoverageSnapshot("v1.8 routed requirements", 8)
_V1_9_COVERAGE = CoverageSnapshot("v1.9 routed requirements", 3, mapped=3, complete=9, pending=0)
_V1_10_COVERAGE = CoverageSnapshot("v1.10 routed requirements", 3, mapped=3, complete=9, pending=0)
_V1_11_COVERAGE = CoverageSnapshot("v1.11 routed requirements", 4, mapped=4, complete=8, pending=0)
_V1_12_COVERAGE = CoverageSnapshot("v1.12 routed requirements", 3, mapped=3, complete=9, pending=0)
_V1_13_COVERAGE = CoverageSnapshot("v1.13 routed requirements", 9, mapped=9, complete=9, pending=0)
_V1_30_COVERAGE = CoverageSnapshot("v1.30 routed requirements", 8, mapped=8, complete=5, pending=3)


def test_v1_8_followup_route_truth_is_recorded_in_roadmap_and_requirements() -> None:
    assert_contains_all(
        _ROADMAP_TEXT,
        "## v1.8: Operational Continuity Automation, Formal-Root Sustainment & Hotspot Round 2",
        "**Milestone status:** `Phase 51 -> 55 complete (2026-03-21)`",
        "**Default next command:** `$gsd-progress`",
        "### Phase 55: Mega-test topicization round 2 and repo-wide typing-metric stratification",
    )
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_checkbox_markers(*_V1_8_TRACES),
        *requirement_table_markers(_V1_8_TRACES[0], _V1_8_TRACES[-1]),
        *_V1_8_COVERAGE.markers(),
    )


def test_v1_9_closeout_package_and_project_pointers_are_consistent() -> None:
    assert_contains_all(
        _ROADMAP_TEXT,
        "## v1.9: Shared Backoff Neutralization & Cross-Plane Retry Hygiene",
        "**Milestone status:** `Phase 56 complete (2026-03-22)`",
        "**Default next command:** `$gsd-complete-milestone v1.9`",
        "### Phase 56: Shared backoff neutralization and cross-plane retry hygiene",
        "**Plans**: 3/3 complete",
    )
    _assert_promoted_closeout_package(_ROADMAP_TEXT, "56-SUMMARY.md", "56-VERIFICATION.md")
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_checkbox_markers(*_V1_9_TRACES),
        *requirement_table_markers(*_V1_9_TRACES),
        *_V1_9_COVERAGE.markers(),
    )
    assert_contains_all(
        _PROJECT_TEXT,
        "## Planned Milestone (v1.8)",
        "## Planned Milestone (v1.9)",
        "**Current status:** `Phase 56 complete (2026-03-22)`",
        ".planning/reviews/V1_9_MILESTONE_SEED.md",
        ".planning/phases/56-shared-backoff-neutralization-and-cross-plane-retry-hygiene/56-01-PLAN.md",
        ".planning/phases/56-shared-backoff-neutralization-and-cross-plane-retry-hygiene/56-SUMMARY.md",
        "$gsd-complete-milestone v1.9",
    )


def test_v1_10_closeout_package_and_project_pointers_are_consistent() -> None:
    assert_contains_all(
        _ROADMAP_TEXT,
        "## v1.10: Command-Result Typed Outcome & Reason-Code Hardening",
        "**Milestone status:** `Phase 57 complete (2026-03-22)`",
        "**Default next command:** `$gsd-complete-milestone v1.10`",
        "### Phase 57: Command-result typed outcome and reason-code hardening",
        "**Plans**: 3/3 complete",
    )
    _assert_promoted_closeout_package(_ROADMAP_TEXT, "57-SUMMARY.md", "57-VERIFICATION.md")
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_checkbox_markers(*_V1_10_TRACES),
        *requirement_table_markers(*_V1_10_TRACES),
        *_V1_10_COVERAGE.markers(),
    )
    assert_contains_all(
        _PROJECT_TEXT,
        "## Planned Milestone (v1.10)",
        "**Current status:** `Phase 57 complete (2026-03-22)`",
        ".planning/reviews/V1_10_MILESTONE_SEED.md",
        ".planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-01-PLAN.md",
        ".planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-SUMMARY.md",
        "$gsd-complete-milestone v1.10",
    )


def test_v1_11_closeout_package_and_project_pointers_are_consistent() -> None:
    assert_contains_all(
        _ROADMAP_TEXT,
        "## v1.11: Repository Audit Refresh & Next-Wave Remediation Routing",
        "**Milestone status:** `Phase 58 complete (2026-03-22)`",
        "**Default next command:** `$gsd-complete-milestone v1.11`",
        "### Phase 58: Repository audit refresh and next-wave routing",
        "**Plans**: 3/3 complete",
    )
    _assert_promoted_closeout_package(_ROADMAP_TEXT, "58-SUMMARY.md", "58-VERIFICATION.md")
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_checkbox_markers(*_V1_11_TRACES),
        *requirement_table_markers(*_V1_11_TRACES),
        *_V1_11_COVERAGE.markers(),
    )


def test_v1_12_to_v1_13_archived_route_truth_uses_promoted_evidence_only() -> None:
    assert_contains_all(
        _ROADMAP_TEXT,
        "## v1.12: Verification Localization & Governance Guard Topicization",
        "**Archive status:** `archived / evidence-ready (2026-03-22)`",
        ".planning/v1.12-MILESTONE-AUDIT.md",
        ".planning/reviews/V1_12_EVIDENCE_INDEX.md",
        "### Phase 59: Verification localization and governance guard topicization",
        "**Plans**: 3/3 complete",
        "## v1.13: Tooling Truth Decomposition, Formal-Home Slimming & Naming/Discoverability Convergence",
        ".planning/v1.13-MILESTONE-AUDIT.md",
        ".planning/reviews/V1_15_EVIDENCE_INDEX.md",
        ".planning/milestones/v1.13-ROADMAP.md",
        ".planning/milestones/v1.13-REQUIREMENTS.md",
        "### Phase 60: Tooling truth decomposition and file-governance maintainability",
        "**Plans**: 3 completed",
        "60-01: decompose the file-matrix checker into thin root and internal truth families",
        "60-02: topicize toolchain truth guards by stable concern family",
        "60-03: freeze tooling topology in governance truth and focused guards",
    )
    _assert_promoted_closeout_package(_ROADMAP_TEXT, "59-SUMMARY.md", "59-VERIFICATION.md")
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_checkbox_markers(*_V1_12_TRACES),
        *requirement_table_markers(*_V1_12_TRACES),
        *_V1_12_COVERAGE.markers(),
        *requirement_checkbox_markers(*_V1_13_TRACES),
        *_V1_13_COVERAGE.markers(),
    )
    assert_contains_all(
        _PROJECT_TEXT,
        "## Archived Milestone (v1.13)",
        "**Current status:** `archived / evidence-ready (2026-03-22)`",
        ".planning/v1.13-MILESTONE-AUDIT.md",
        ".planning/reviews/V1_15_EVIDENCE_INDEX.md",
        ".planning/milestones/v1.13-ROADMAP.md",
    )
    assert ".planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-01-PLAN.md" not in _PROJECT_TEXT



def test_machine_readable_route_contracts_point_to_active_v1_30_and_latest_archived_v1_29() -> None:
    contracts = assert_machine_readable_route_contracts()
    requirements_contract = _as_mapping(contracts["REQUIREMENTS"])
    requirements_active = _as_optional_mapping(requirements_contract["active_milestone"])
    milestones_contract = _as_mapping(contracts["MILESTONES"])
    milestones_active = _as_optional_mapping(milestones_contract["active_milestone"])
    milestones_latest_archived = _as_mapping(milestones_contract["latest_archived"])
    milestones_previous_archived = _as_mapping(milestones_contract["previous_archived"])
    state_contract = _as_mapping(contracts["STATE"])
    state_bootstrap = _as_mapping(state_contract["bootstrap"])

    assert requirements_active is not None
    assert requirements_active["version"] == "v1.30"
    assert requirements_active["phase"] == "108"
    assert requirements_active["route_mode"] == CURRENT_ROUTE_MODE
    assert milestones_active is not None
    assert milestones_active["version"] == "v1.30"
    assert milestones_active["phase"] == "108"
    assert milestones_active["route_mode"] == CURRENT_ROUTE_MODE
    assert milestones_latest_archived["version"] == "v1.29"
    assert milestones_latest_archived["phase"] == "105"
    assert milestones_previous_archived["version"] == "v1.28"
    assert state_bootstrap["current_route"] == CURRENT_ROUTE_MODE
    assert state_bootstrap["default_next_command"] == CURRENT_MILESTONE_DEFAULT_NEXT
    assert state_bootstrap["latest_archived_evidence_pointer"] == LATEST_ARCHIVED_EVIDENCE_PATH


def test_historical_route_truth_replaces_legacy_live_state_wording() -> None:
    assert_contains_all(
        _MILESTONES_TEXT,
        HISTORICAL_CLOSEOUT_ROUTE_TRUTH,
        HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH,
    )
    for text in (_ROADMAP_TEXT, _REQUIREMENTS_TEXT):
        assert_contains_all(
            text,
            HISTORICAL_CLOSEOUT_ROUTE_TRUTH,
            HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH,
        )
    for text in (_MILESTONES_TEXT, _ROADMAP_TEXT, _REQUIREMENTS_TEXT):
        assert_not_contains_any(
            text,
            "current governance state =",
            "当前治理状态已切换为",
            "当前治理状态现已切换为",
            "live governance state",
        )



def test_current_v1_30_active_state_and_archive_pointers_align() -> None:
    _assert_current_route_truth(_PROJECT_TEXT, _ROADMAP_TEXT, _STATE_TEXT)
    assert_contains_all(
        _PROJECT_TEXT,
        CURRENT_MILESTONE_HEADER,
        LATEST_ARCHIVED_PROJECT_HEADER,
        PREVIOUS_ARCHIVED_PROJECT_HEADER,
        f"**Current status:** `{CURRENT_MILESTONE_STATUS}`",
        f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`",
    )
    assert_contains_all(
        _ROADMAP_TEXT,
        "## v1.30: Protocol Hotspot Convergence, Transport De-friendization & Snapshot Surface Slimming",
        "### Phase 107: REST/auth/status hotspot convergence and support-surface slimming",
        "### Phase 108: MQTT transport-runtime de-friendization",
        "### Phase 109: Anonymous-share manager inward decomposition",
        "### Phase 110: Runtime snapshot surface reduction and milestone closeout",
        CURRENT_MILESTONE_DEFAULT_NEXT,
        ".planning/reviews/V1_29_EVIDENCE_INDEX.md",
        ".planning/phases/107-rest-auth-status-hotspot-convergence-and-support-surface-slimming/{107-01-SUMMARY.md,107-02-SUMMARY.md,107-03-SUMMARY.md,107-VERIFICATION.md,107-VALIDATION.md}",
        ".planning/phases/108-mqtt-transport-runtime-de-friendization/{108-01-SUMMARY.md,108-02-SUMMARY.md,108-03-SUMMARY.md,108-VERIFICATION.md,108-VALIDATION.md}",
        ".planning/phases/108-mqtt-transport-runtime-de-friendization/{108-01-SUMMARY.md,108-02-SUMMARY.md,108-03-SUMMARY.md,108-VERIFICATION.md,108-VALIDATION.md}",
    )
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        CURRENT_MILESTONE_HEADER,
        *requirement_table_markers(*_V1_30_TRACES),
        *_V1_30_COVERAGE.markers(),
        LATEST_ARCHIVED_PROJECT_HEADER,
    )
    assert_contains_all(
        _STATE_TEXT,
        f"**Current milestone:** `{CURRENT_MILESTONE_STATE_LABEL}`",
        f"**Current mode:** `{CURRENT_ROUTE_MODE}`",
        CURRENT_MILESTONE_DEFAULT_NEXT,
        LATEST_ARCHIVED_AUDIT_PATH,
        LATEST_ARCHIVED_EVIDENCE_PATH,
    )
    assert CURRENT_MILESTONE_STATUS == "active / Phase 108 complete / continuation-ready (2026-03-30)"

