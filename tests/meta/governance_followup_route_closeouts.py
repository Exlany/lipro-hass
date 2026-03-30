"""Archived follow-up route and closeout truth guards."""

from __future__ import annotations

from .governance_contract_helpers import (
    _assert_project_allows_post_v1_4_next_step,
    _assert_state_keeps_forward_progress_commands,
    _assert_state_reflects_post_v1_4_continuation,
)
from .governance_current_truth import CURRENT_MILESTONE_DEFAULT_NEXT
from .governance_followup_route_specs import (
    CoverageSnapshot,
    RequirementTrace,
    assert_contains_all,
    load_planning_docs_snapshot,
    requirement_table_markers,
)
from .governance_promoted_assets import _assert_promoted_phase_assets

_SNAPSHOT = load_planning_docs_snapshot(include_reviews=True)
_ROADMAP_TEXT = _SNAPSHOT.roadmap
_REQUIREMENTS_TEXT = _SNAPSHOT.requirements
_PROJECT_TEXT = _SNAPSHOT.project
_STATE_TEXT = _SNAPSHOT.state
_RESIDUAL_TEXT = _SNAPSHOT.residual or ""
_KILL_TEXT = _SNAPSHOT.kill or ""

_PHASE_36_TRACES = (
    RequirementTrace("HOT-10", "36"),
    RequirementTrace("ERR-08", "36"),
    RequirementTrace("TYP-09", "36"),
)
_PHASE_37_TRACES = (
    RequirementTrace("TST-06", "37"),
    RequirementTrace("GOV-30", "37"),
    RequirementTrace("QLT-09", "37"),
)
_PHASE_38_TRACES = (
    RequirementTrace("RES-08", "38"),
    RequirementTrace("QLT-10", "38"),
    RequirementTrace("GOV-31", "38"),
)
_PHASE_39_TRACES = (
    RequirementTrace("GOV-32", "39"),
    RequirementTrace("DOC-03", "39"),
    RequirementTrace("CTRL-08", "39"),
    RequirementTrace("RES-09", "39"),
    RequirementTrace("TST-07", "39"),
)
_PHASE_40_TRACES = (
    RequirementTrace("GOV-33", "40"),
    RequirementTrace("QLT-11", "40"),
    RequirementTrace("CTRL-09", "40"),
    RequirementTrace("ERR-10", "40"),
    RequirementTrace("RES-10", "40"),
)
_PHASE_42_TO_45_TRACES = (
    RequirementTrace("GOV-34", "42", status="Completed"),
    RequirementTrace("QLT-12", "42", status="Completed"),
    RequirementTrace("QLT-13", "42", status="Completed"),
    RequirementTrace("QLT-14", "42", status="Completed"),
    RequirementTrace("ARC-04", "43", status="Completed"),
    RequirementTrace("CTRL-10", "43", status="Completed"),
    RequirementTrace("RUN-07", "43", status="Completed"),
    RequirementTrace("GOV-35", "44", status="Completed"),
    RequirementTrace("RES-11", "44", status="Completed"),
    RequirementTrace("DOC-04", "44", status="Completed"),
    RequirementTrace("HOT-11", "45", status="Completed"),
    RequirementTrace("ERR-11", "45", status="Completed"),
    RequirementTrace("TYP-10", "45", status="Completed"),
    RequirementTrace("QLT-15", "45", status="Completed"),
)
_PHASE_46_TRACES = (
    RequirementTrace("GOV-36", "46"),
    RequirementTrace("ARC-05", "46"),
    RequirementTrace("DOC-05", "46"),
    RequirementTrace("RES-12", "46"),
    RequirementTrace("TST-08", "46"),
    RequirementTrace("TYP-11", "46"),
    RequirementTrace("QLT-16", "46"),
)

_V1_4_COVERAGE = CoverageSnapshot("v1.4 requirements + fresh-audit continuation", 18, mapped=18, complete=18, pending=0)
_V1_5_COVERAGE = CoverageSnapshot("v1.5 routed requirements", 5, mapped=5, complete=5, pending=0)
_V1_6_COVERAGE = CoverageSnapshot("v1.6 routed requirements", 14, mapped=14, complete=14, pending=0)
_V1_7_COVERAGE = CoverageSnapshot("v1.7 routed requirements", 7, mapped=7, complete=7, pending=0)


def test_phase_36_planning_truth_is_consistent() -> None:
    _assert_promoted_phase_assets(
        "36-runtime-root-and-exception-burn-down",
        "36-01-SUMMARY.md",
        "36-02-SUMMARY.md",
        "36-03-SUMMARY.md",
        "36-SUMMARY.md",
        "36-VERIFICATION.md",
    )

    assert_contains_all(
        _ROADMAP_TEXT,
        "### Phase 36: Runtime root and exception burn-down",
        "**Requirements**: [HOT-10, ERR-08, TYP-09]",
        "**Status**: Complete (`2026-03-18`)",
        "**Plans**: 3/3 complete",
    )
    assert_contains_all(_REQUIREMENTS_TEXT, *requirement_table_markers(*_PHASE_36_TRACES))
    assert_contains_all(_PROJECT_TEXT, "## Phase 36 Runtime Root Burn-Down Update")
    assert "## Recommended Next Command" in _STATE_TEXT


def test_phase_37_planning_truth_is_consistent() -> None:
    _assert_promoted_phase_assets(
        "37-test-topology-and-derived-truth-convergence",
        "37-01-SUMMARY.md",
        "37-02-SUMMARY.md",
        "37-03-SUMMARY.md",
        "37-SUMMARY.md",
        "37-VERIFICATION.md",
    )

    assert_contains_all(
        _ROADMAP_TEXT,
        "### Phase 37: Test topology and derived-truth convergence",
        "**Requirements**: [TST-06, GOV-30, QLT-09]",
        "**Status**: Complete (`2026-03-18`)",
        "**Plans**: 3/3 complete",
    )
    assert_contains_all(_REQUIREMENTS_TEXT, *requirement_table_markers(*_PHASE_37_TRACES))
    assert_contains_all(_PROJECT_TEXT, "## Phase 37 Test Topology & Derived-Truth Update")
    _assert_project_allows_post_v1_4_next_step(_PROJECT_TEXT)
    _assert_state_keeps_forward_progress_commands(_STATE_TEXT)


def test_phase_38_planning_truth_is_consistent() -> None:
    _assert_promoted_phase_assets(
        "38-external-boundary-residual-retirement-and-quality-signal-hardening",
        "38-SUMMARY.md",
        "38-VERIFICATION.md",
    )

    assert_contains_all(
        _ROADMAP_TEXT,
        "### Phase 38: External-boundary residual retirement and quality-signal hardening",
        "**Requirements**: [RES-08, QLT-10, GOV-31]",
        "**Status**: Complete (`2026-03-18`)",
        "**Plans**: 3/3 complete",
    )
    assert_contains_all(_REQUIREMENTS_TEXT, *requirement_table_markers(*_PHASE_38_TRACES))
    assert_contains_all(_PROJECT_TEXT, "## Phase 38 External-Boundary Residual & Quality-Signal Hardening Update")
    _assert_project_allows_post_v1_4_next_step(_PROJECT_TEXT)
    _assert_state_reflects_post_v1_4_continuation(_STATE_TEXT)
    _assert_state_keeps_forward_progress_commands(_STATE_TEXT)
    assert "`Generic backoff helper leak` 已在 Phase 56 关闭" in _RESIDUAL_TEXT
    assert _RESIDUAL_TEXT.count("## Phase 38 Residual Delta") == 1


def test_phase_39_planning_truth_is_consistent() -> None:
    _assert_promoted_phase_assets(
        "39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition",
        "39-SUMMARY.md",
        "39-VERIFICATION.md",
    )

    assert_contains_all(
        _ROADMAP_TEXT,
        "### Phase 39: Governance current-story convergence, control-home clarification, and mega-test decomposition",
        "**Requirements**: [GOV-32, DOC-03, CTRL-08, RES-09, TST-07]",
        "**Status**: Complete (`2026-03-19`)",
        "**Plans**: 6/6 complete",
    )
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_table_markers(*_PHASE_39_TRACES),
        *_V1_4_COVERAGE.markers(),
    )
    assert_contains_all(
        _PROJECT_TEXT,
        "## Archived Milestone (v1.4)",
        "## Phase 39 Governance Current-Story & Mega-Test Closeout Update",
    )
    _assert_project_allows_post_v1_4_next_step(_PROJECT_TEXT)
    _assert_state_reflects_post_v1_4_continuation(_STATE_TEXT)
    _assert_state_keeps_forward_progress_commands(_STATE_TEXT)
    assert "## Phase 39 Residual Delta" in _RESIDUAL_TEXT
    assert "## Phase 39 Status Update" in _KILL_TEXT


def test_phase_40_closeout_truth_is_consistent() -> None:
    assert_contains_all(
        _ROADMAP_TEXT,
        "## v1.5: Governance Truth Consolidation & Control-Surface Finalization",
        "**Archive status:** `shipped / archived (2026-03-19)`",
        "40-VALIDATION.md",
    )
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_table_markers(*_PHASE_40_TRACES),
        *_V1_5_COVERAGE.markers(),
    )
    assert_contains_all(_PROJECT_TEXT, "## Archived Milestone (v1.5)", ".planning/reviews/V1_5_EVIDENCE_INDEX.md")
    _assert_project_allows_post_v1_4_next_step(_PROJECT_TEXT)
    assert ".planning/v1.5-MILESTONE-AUDIT.md" in _STATE_TEXT
    assert ".planning/reviews/V1_5_EVIDENCE_INDEX.md" in _STATE_TEXT
    _assert_state_reflects_post_v1_4_continuation(_STATE_TEXT)
    _assert_state_keeps_forward_progress_commands(_STATE_TEXT)


def test_phase_42_to_45_closeout_truth_is_consistent() -> None:
    assert_contains_all(
        _ROADMAP_TEXT,
        "## v1.6: Delivery Trust Hardening, Runtime Boundary Decoupling & Maintainability Closure",
        "**Archive status:** `archived / evidence-ready (2026-03-20)`",
        "45-VERIFICATION.md",
    )
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_table_markers(*_PHASE_42_TO_45_TRACES),
        *_V1_6_COVERAGE.markers(),
    )
    assert_contains_all(_PROJECT_TEXT, "## Archived Milestone (v1.6)", ".planning/reviews/V1_6_EVIDENCE_INDEX.md")
    _assert_project_allows_post_v1_4_next_step(_PROJECT_TEXT)
    assert ".planning/v1.6-MILESTONE-AUDIT.md" in _STATE_TEXT
    assert ".planning/reviews/V1_6_EVIDENCE_INDEX.md" in _STATE_TEXT
    assert "$gsd-progress" in _STATE_TEXT
    _assert_state_reflects_post_v1_4_continuation(_STATE_TEXT)
    _assert_state_keeps_forward_progress_commands(_STATE_TEXT)


def test_phase_46_audit_truth_is_consistent() -> None:
    assert_contains_all(
        _ROADMAP_TEXT,
        "## v1.7: Full-Spectrum Repository Audit, Open-Source Maturity & Remediation Routing",
        "**Milestone status:** `Phase 46 audit complete; Phase 47 -> 50 complete (2026-03-21)`",
        "**Status**: Complete (`2026-03-20`)",
        "**Promoted audit package**: `46-AUDIT.md`, `46-SCORE-MATRIX.md`, `46-REMEDIATION-ROADMAP.md`, `46-SUMMARY.md`, `46-VERIFICATION.md`",
        "**Follow-up route source**: `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md`",
    )
    assert_contains_all(
        _REQUIREMENTS_TEXT,
        *requirement_table_markers(*_PHASE_46_TRACES),
        *_V1_7_COVERAGE.markers(),
    )
    assert_contains_all(
        _PROJECT_TEXT,
        "## Completed Follow-up Milestone (v1.7)",
        "**Current status:** `Phase 46 -> 50 complete (2026-03-21)`",
        "**Promoted audit package:** `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-AUDIT.md`",
        "**Next route source:** `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md`",
        ".planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-SUMMARY.md",
        ".planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-VERIFICATION.md",
    )
    assert "`Phase 46` 已于 `2026-03-20` 执行完成" in _STATE_TEXT
    assert "46-REMEDIATION-ROADMAP.md" in _STATE_TEXT
    assert CURRENT_MILESTONE_DEFAULT_NEXT in _STATE_TEXT
    assert "$gsd-progress" in _STATE_TEXT
