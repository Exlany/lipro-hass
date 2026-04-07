"""Governance guards for continuity routing and archived-milestone follow-up truth."""

from __future__ import annotations

from .governance_contract_helpers import _assert_state_keeps_forward_progress_commands
from .governance_followup_route_specs import (
    CoverageSnapshot,
    RequirementTrace,
    assert_contains_all,
    load_planning_docs_snapshot,
    requirement_checkbox_markers,
    requirement_table_markers,
)
from .governance_promoted_assets import (
    _assert_phase_assets_not_promoted,
    _assert_promoted_phase_assets,
)

_SNAPSHOT = load_planning_docs_snapshot()
_ROADMAP_TEXT = _SNAPSHOT.roadmap
_REQUIREMENTS_TEXT = _SNAPSHOT.requirements
_PROJECT_TEXT = _SNAPSHOT.project
_STATE_TEXT = _SNAPSHOT.state

_PHASE_28_TO_31_TRACES = (
    RequirementTrace("GOV-22", "28"),
    RequirementTrace("QLT-04", "28"),
    RequirementTrace("HOT-06", "29"),
    RequirementTrace("RES-05", "29"),
    RequirementTrace("TST-03", "29"),
    RequirementTrace("TYP-06", "30"),
    RequirementTrace("ERR-04", "30"),
    RequirementTrace("TYP-07", "31"),
    RequirementTrace("ERR-05", "31"),
    RequirementTrace("GOV-23", "31"),
)
_PHASE_32_TRACES = (
    RequirementTrace("GOV-24", "32"),
    RequirementTrace("QLT-05", "32"),
    RequirementTrace("GOV-25", "32"),
    RequirementTrace("GOV-26", "32"),
    RequirementTrace("HOT-07", "32"),
    RequirementTrace("TST-04", "32"),
    RequirementTrace("TYP-08", "32"),
    RequirementTrace("ERR-06", "32"),
    RequirementTrace("RES-06", "32"),
)
_PHASE_33_TRACES = (
    RequirementTrace("ARC-03", "33"),
    RequirementTrace("CTRL-07", "33"),
    RequirementTrace("HOT-08", "33"),
    RequirementTrace("ERR-07", "33"),
    RequirementTrace("TST-05", "33"),
    RequirementTrace("QLT-06", "33"),
    RequirementTrace("GOV-27", "33"),
    RequirementTrace("GOV-28", "33"),
    RequirementTrace("QLT-07", "33"),
)
_PHASE_34_TRACES = (
    RequirementTrace("GOV-29", "34"),
    RequirementTrace("QLT-08", "34"),
)
_PHASE_35_TRACES = (
    RequirementTrace("HOT-09", "35"),
    RequirementTrace("RES-07", "35"),
)

_V1_3_COVERAGE = CoverageSnapshot("v1.3 routed requirements", 29, mapped=29, complete=29, pending=0)


def test_phase_28_to_31_continuation_assets_and_tracking_truth_are_synced() -> None:
    _assert_phase_assets_not_promoted(
        "28-release-trust-gate-completion-and-maintainer-resilience",
        "28-01-SUMMARY.md",
        "28-VERIFICATION.md",
        "28-VALIDATION.md",
    )
    _assert_phase_assets_not_promoted(
        "29-rest-child-facade-slimming-and-test-topicization",
        "29-01-SUMMARY.md",
        "29-VERIFICATION.md",
        "29-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "30-protocol-control-typed-contract-tightening",
        "30-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "31-runtime-service-typed-budget-and-exception-closure",
        "31-VERIFICATION.md",
    )

    for heading, next_heading, plan_count in (
        (
            "### Phase 28: Release trust gate completion and maintainer resilience",
            "### Phase 29:",
            "3/3 complete",
        ),
        (
            "### Phase 29: REST child-façade slimming and test topicization",
            "### Phase 30:",
            "3/3 complete",
        ),
        (
            "### Phase 30: Protocol/control typed contract tightening",
            "### Phase 31:",
            "3/3 complete",
        ),
        (
            "### Phase 31: Runtime/service typed budget and exception closure",
            None,
            "4/4 complete",
        ),
    ):
        tail = _ROADMAP_TEXT.split(heading, maxsplit=1)[1]
        section = tail if next_heading is None else tail.split(next_heading, maxsplit=1)[0]
        assert "**Status**: Complete (`2026-03-17`)" in section
        assert f"**Plans**: {plan_count}" in section

    assert_contains_all(_REQUIREMENTS_TEXT, *requirement_table_markers(*_PHASE_28_TO_31_TRACES))
    assert "## Recommended Next Command" in _STATE_TEXT
    assert "$gsd-progress" in _STATE_TEXT


def test_phase_32_completion_truth_is_consistent() -> None:
    _assert_promoted_phase_assets(
        "32-truth-convergence-gate-honesty-and-quality-10-closeout",
        "32-VERIFICATION.md",
    )

    assert_contains_all(
        _ROADMAP_TEXT,
        "**Execution Scope:** `Phase 25 -> Phase 32`",
        "### Phase 32: Truth convergence, gate honesty, and quality-10 closeout",
        "**Requirements**: [GOV-24, QLT-05, GOV-25, GOV-26, HOT-07, TST-04, TYP-08, ERR-06, RES-06]",
        "**Status**: Complete (`2026-03-18`)",
        "**Plans**: 5/5 complete",
        "- [x] 32-05: close hotspot slimming, mega-test topicization, typed/exception debt, and residual honesty",
    )
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_checkbox_markers(*_PHASE_32_TRACES),
        *requirement_table_markers(*_PHASE_32_TRACES),
        *_V1_3_COVERAGE.markers(),
    )
    assert_contains_all(
        _PROJECT_TEXT,
        "## v1.3 Closeout & Post-closeout Continuation",
        "`Phase 32` — truth convergence, gate honesty, and quality-10 closeout",
    )
    _assert_state_keeps_forward_progress_commands(_STATE_TEXT)


def test_phase_33_planning_truth_is_consistent() -> None:
    _assert_promoted_phase_assets(
        "33-contract-truth-unification-hotspot-slimming-and-productization-hardening",
        "33-SUMMARY.md",
        "33-VERIFICATION.md",
    )

    assert_contains_all(
        _ROADMAP_TEXT,
        "### Phase 33: Contract-truth unification, hotspot slimming, and productization hardening",
        "**Requirements**: [ARC-03, CTRL-07, HOT-08, ERR-07, TST-05, QLT-06, GOV-27, GOV-28, QLT-07]",
        "**Status**: Complete (`2026-03-18`)",
        "**Plans**: 6/6 complete",
    )
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_checkbox_markers(*_PHASE_33_TRACES),
        *requirement_table_markers(*_PHASE_33_TRACES),
    )
    assert_contains_all(_PROJECT_TEXT, "## Phase 33 Audit-Driven Continuation", "**Execution promise:**")
    _assert_state_keeps_forward_progress_commands(_STATE_TEXT)


def test_phase_34_planning_truth_is_consistent() -> None:
    _assert_promoted_phase_assets(
        "34-continuity-and-hard-release-gates",
        "34-SUMMARY.md",
        "34-VERIFICATION.md",
    )

    assert_contains_all(
        _ROADMAP_TEXT,
        "### Phase 34: Continuity and hard release gates",
        "**Requirements**: [GOV-29, QLT-08]",
        "**Status**: Complete (`2026-03-18`)",
        "**Plans**: 3/3 complete",
        "- [x] 34-01: formalize continuity, custody, and freeze-escalation contracts",
        "- [x] 34-02: add artifact signing and hard release-trust gates",
        "- [x] 34-03: converge public docs, runbook, CODEOWNERS, and guards on continuity/release truth",
    )
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_checkbox_markers(*_PHASE_34_TRACES),
        *requirement_table_markers(*_PHASE_34_TRACES),
    )
    assert_contains_all(_PROJECT_TEXT, "## Phase 34 Seed Hardening Update")
    _assert_state_keeps_forward_progress_commands(_STATE_TEXT)


def test_phase_35_planning_truth_is_consistent() -> None:
    _assert_promoted_phase_assets(
        "35-protocol-hotspot-final-slimming",
        "35-01-SUMMARY.md",
        "35-02-SUMMARY.md",
        "35-03-SUMMARY.md",
        "35-SUMMARY.md",
        "35-VERIFICATION.md",
    )

    assert_contains_all(
        _ROADMAP_TEXT,
        "### Phase 35: Protocol hotspot final slimming",
        "**Requirements**: [HOT-09, RES-07]",
        "**Status**: Complete (`2026-03-18`)",
        "**Plans**: 3/3 complete",
    )
    assert_contains_all(_REQUIREMENTS_TEXT, *requirement_table_markers(*_PHASE_35_TRACES))
    assert_contains_all(_PROJECT_TEXT, "## Phase 35 Protocol Hotspot Slimming Update")
    assert "## Recommended Next Command" in _STATE_TEXT
