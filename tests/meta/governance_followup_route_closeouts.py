"""Archived follow-up route and closeout truth guards."""

from __future__ import annotations

from .test_governance_closeout_guards import (
    _ROOT,
    _assert_project_allows_post_v1_4_next_step,
    _assert_promoted_phase_assets,
    _assert_state_keeps_forward_progress_commands,
    _assert_state_reflects_post_v1_4_continuation,
)


def test_phase_36_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "36-runtime-root-and-exception-burn-down",
        "36-01-SUMMARY.md",
        "36-02-SUMMARY.md",
        "36-03-SUMMARY.md",
        "36-SUMMARY.md",
        "36-VERIFICATION.md",
    )

    assert "### Phase 36: Runtime root and exception burn-down" in roadmap_text
    assert "**Requirements**: [HOT-10, ERR-08, TYP-09]" in roadmap_text
    assert "**Status**: Complete (`2026-03-18`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "| HOT-10 | Phase 36 | Complete |" in requirements_text
    assert "| ERR-08 | Phase 36 | Complete |" in requirements_text
    assert "| TYP-09 | Phase 36 | Complete |" in requirements_text
    assert "## Phase 36 Runtime Root Burn-Down Update" in project_text
    assert "## Recommended Next Command" in state_text


def test_phase_37_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "37-test-topology-and-derived-truth-convergence",
        "37-01-SUMMARY.md",
        "37-02-SUMMARY.md",
        "37-03-SUMMARY.md",
        "37-SUMMARY.md",
        "37-VERIFICATION.md",
    )

    assert "### Phase 37: Test topology and derived-truth convergence" in roadmap_text
    assert "**Requirements**: [TST-06, GOV-30, QLT-09]" in roadmap_text
    assert "**Status**: Complete (`2026-03-18`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "| TST-06 | Phase 37 | Complete |" in requirements_text
    assert "| GOV-30 | Phase 37 | Complete |" in requirements_text
    assert "| QLT-09 | Phase 37 | Complete |" in requirements_text
    assert "## Phase 37 Test Topology & Derived-Truth Update" in project_text
    _assert_project_allows_post_v1_4_next_step(project_text)
    _assert_state_keeps_forward_progress_commands(state_text)


def test_phase_38_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )

    _assert_promoted_phase_assets(
        "38-external-boundary-residual-retirement-and-quality-signal-hardening",
        "38-SUMMARY.md",
        "38-VERIFICATION.md",
    )

    assert "### Phase 38: External-boundary residual retirement and quality-signal hardening" in roadmap_text
    assert "**Requirements**: [RES-08, QLT-10, GOV-31]" in roadmap_text
    assert "**Status**: Complete (`2026-03-18`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "| RES-08 | Phase 38 | Complete |" in requirements_text
    assert "| QLT-10 | Phase 38 | Complete |" in requirements_text
    assert "| GOV-31 | Phase 38 | Complete |" in requirements_text
    assert "## Phase 38 External-Boundary Residual & Quality-Signal Hardening Update" in project_text
    _assert_project_allows_post_v1_4_next_step(project_text)
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)
    assert "`Generic backoff helper leak` 已在 Phase 56 关闭" in residual_text
    assert "## Phase 38 Residual Delta" in residual_text
    assert "## Phase 38 Residual Delta" in residual_text


def test_phase_39_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition",
        "39-SUMMARY.md",
        "39-VERIFICATION.md",
    )

    assert "### Phase 39: Governance current-story convergence, control-home clarification, and mega-test decomposition" in roadmap_text
    assert "**Requirements**: [GOV-32, DOC-03, CTRL-08, RES-09, TST-07]" in roadmap_text
    assert "**Status**: Complete (`2026-03-19`)" in roadmap_text
    assert "**Plans**: 6/6 complete" in roadmap_text

    for needle in (
        "| GOV-32 | Phase 39 | Complete |",
        "| DOC-03 | Phase 39 | Complete |",
        "| CTRL-08 | Phase 39 | Complete |",
        "| RES-09 | Phase 39 | Complete |",
        "| TST-07 | Phase 39 | Complete |",
        "- v1.4 requirements + fresh-audit continuation: 18 total",
        "- Current mapped: 18",
        "- Current complete: 18",
        "- Current pending: 0",
    ):
        assert needle in requirements_text

    assert "## Archived Milestone (v1.4)" in project_text
    assert "## Phase 39 Governance Current-Story & Mega-Test Closeout Update" in project_text
    _assert_project_allows_post_v1_4_next_step(project_text)
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)
    assert "## Phase 39 Residual Delta" in residual_text
    assert "## Phase 39 Status Update" in kill_text


def test_phase_40_closeout_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    assert "## v1.5: Governance Truth Consolidation & Control-Surface Finalization" in roadmap_text
    assert "**Archive status:** `shipped / archived (2026-03-19)`" in roadmap_text
    assert "40-VALIDATION.md" in roadmap_text

    for needle in (
        "| GOV-33 | Phase 40 | Complete |",
        "| QLT-11 | Phase 40 | Complete |",
        "| CTRL-09 | Phase 40 | Complete |",
        "| ERR-10 | Phase 40 | Complete |",
        "| RES-10 | Phase 40 | Complete |",
        "- v1.5 routed requirements: 5 total",
        "- Current mapped: 5",
        "- Current complete: 5",
        "- Current pending: 0",
    ):
        assert needle in requirements_text

    assert "## Archived Milestone (v1.5)" in project_text
    _assert_project_allows_post_v1_4_next_step(project_text)
    assert ".planning/reviews/V1_5_EVIDENCE_INDEX.md" in project_text

    assert ".planning/v1.5-MILESTONE-AUDIT.md" in state_text
    assert ".planning/reviews/V1_5_EVIDENCE_INDEX.md" in state_text
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)


def test_phase_42_to_45_closeout_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    assert "## v1.6: Delivery Trust Hardening, Runtime Boundary Decoupling & Maintainability Closure" in roadmap_text
    assert "**Archive status:** `archived / evidence-ready (2026-03-20)`" in roadmap_text
    assert "45-VERIFICATION.md" in roadmap_text

    for needle in (
        "| GOV-34 | Phase 42 | Completed |",
        "| QLT-12 | Phase 42 | Completed |",
        "| QLT-13 | Phase 42 | Completed |",
        "| QLT-14 | Phase 42 | Completed |",
        "| ARC-04 | Phase 43 | Completed |",
        "| CTRL-10 | Phase 43 | Completed |",
        "| RUN-07 | Phase 43 | Completed |",
        "| GOV-35 | Phase 44 | Completed |",
        "| RES-11 | Phase 44 | Completed |",
        "| DOC-04 | Phase 44 | Completed |",
        "| HOT-11 | Phase 45 | Completed |",
        "| ERR-11 | Phase 45 | Completed |",
        "| TYP-10 | Phase 45 | Completed |",
        "| QLT-15 | Phase 45 | Completed |",
        "- v1.6 routed requirements: 14 total",
        "- Current mapped: 14",
        "- Current complete: 14",
        "- Current pending: 0",
    ):
        assert needle in requirements_text

    assert "## Archived Milestone (v1.6)" in project_text
    assert ".planning/reviews/V1_6_EVIDENCE_INDEX.md" in project_text
    _assert_project_allows_post_v1_4_next_step(project_text)

    assert ".planning/v1.6-MILESTONE-AUDIT.md" in state_text
    assert ".planning/reviews/V1_6_EVIDENCE_INDEX.md" in state_text
    assert "$gsd-progress" in state_text
    _assert_state_reflects_post_v1_4_continuation(state_text)
    _assert_state_keeps_forward_progress_commands(state_text)


def test_phase_46_audit_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    assert "## v1.7: Full-Spectrum Repository Audit, Open-Source Maturity & Remediation Routing" in roadmap_text
    assert "**Milestone status:** `Phase 46 audit complete; Phase 47 -> 50 complete (2026-03-21)`" in roadmap_text
    assert "**Status**: Complete (`2026-03-20`)" in roadmap_text
    assert "**Promoted audit package**: `46-AUDIT.md`, `46-SCORE-MATRIX.md`, `46-REMEDIATION-ROADMAP.md`, `46-SUMMARY.md`, `46-VERIFICATION.md`" in roadmap_text
    assert "**Follow-up route source**: `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md`" in roadmap_text

    for needle in (
        "| GOV-36 | Phase 46 | Complete |",
        "| ARC-05 | Phase 46 | Complete |",
        "| DOC-05 | Phase 46 | Complete |",
        "| RES-12 | Phase 46 | Complete |",
        "| TST-08 | Phase 46 | Complete |",
        "| TYP-11 | Phase 46 | Complete |",
        "| QLT-16 | Phase 46 | Complete |",
        "- v1.7 routed requirements: 7 total",
        "- Current mapped: 7",
        "- Current complete: 7",
        "- Current pending: 0",
    ):
        assert needle in requirements_text

    assert "## Completed Follow-up Milestone (v1.7)" in project_text
    assert "**Current status:** `Phase 46 -> 50 complete (2026-03-21)`" in project_text
    assert "**Promoted audit package:** `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-AUDIT.md`" in project_text
    assert "**Next route source:** `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md`" in project_text
    assert ".planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-SUMMARY.md" in project_text
    assert ".planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-VERIFICATION.md" in project_text

    assert "`Phase 46` 已于 `2026-03-20` 执行完成" in state_text
    assert "46-REMEDIATION-ROADMAP.md" in state_text
    assert "$gsd-new-milestone" in state_text
