"""Governance guards for continuity routing and archived-milestone follow-up truth."""

from __future__ import annotations

from .test_governance_closeout_guards import (
    _ROOT,
    _assert_phase_assets_not_promoted,
    _assert_project_allows_post_v1_4_next_step,
    _assert_promoted_phase_assets,
    _assert_state_keeps_forward_progress_commands,
    _assert_state_reflects_post_v1_4_continuation,
)


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

    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

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
        tail = roadmap_text.split(heading, maxsplit=1)[1]
        section = tail if next_heading is None else tail.split(next_heading, maxsplit=1)[0]
        assert "**Status**: Complete (`2026-03-17`)" in section
        assert f"**Plans**: {plan_count}" in section

    for needle in (
        "| GOV-22 | Phase 28 | Complete |",
        "| QLT-04 | Phase 28 | Complete |",
        "| HOT-06 | Phase 29 | Complete |",
        "| RES-05 | Phase 29 | Complete |",
        "| TST-03 | Phase 29 | Complete |",
        "| TYP-06 | Phase 30 | Complete |",
        "| ERR-04 | Phase 30 | Complete |",
        "| TYP-07 | Phase 31 | Complete |",
        "| ERR-05 | Phase 31 | Complete |",
        "| GOV-23 | Phase 31 | Complete |",
    ):
        assert needle in requirements_text

    assert "## Recommended Next Command" in state_text
    assert "$gsd-progress" in state_text


def test_phase_32_completion_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "32-truth-convergence-gate-honesty-and-quality-10-closeout",
        "32-VERIFICATION.md",
    )

    assert "**Execution Scope:** `Phase 25 -> Phase 32`" in roadmap_text
    assert "### Phase 32: Truth convergence, gate honesty, and quality-10 closeout" in roadmap_text
    assert (
        "**Requirements**: [GOV-24, QLT-05, GOV-25, GOV-26, HOT-07, TST-04, TYP-08, ERR-06, RES-06]"
        in roadmap_text
    )
    assert "**Status**: Complete (`2026-03-18`)" in roadmap_text
    assert "**Plans**: 5/5 complete" in roadmap_text
    assert "- [x] 32-05: close hotspot slimming, mega-test topicization, typed/exception debt, and residual honesty" in roadmap_text

    for needle in (
        "- [x] **GOV-24**",
        "- [x] **QLT-05**",
        "- [x] **GOV-25**",
        "- [x] **GOV-26**",
        "- [x] **HOT-07**",
        "- [x] **TST-04**",
        "- [x] **TYP-08**",
        "- [x] **ERR-06**",
        "- [x] **RES-06**",
        "| GOV-24 | Phase 32 | Complete |",
        "| QLT-05 | Phase 32 | Complete |",
        "| GOV-25 | Phase 32 | Complete |",
        "| GOV-26 | Phase 32 | Complete |",
        "| HOT-07 | Phase 32 | Complete |",
        "| TST-04 | Phase 32 | Complete |",
        "| TYP-08 | Phase 32 | Complete |",
        "| ERR-06 | Phase 32 | Complete |",
        "| RES-06 | Phase 32 | Complete |",
    ):
        assert needle in requirements_text

    assert "- v1.3 routed requirements: 29 total" in requirements_text
    assert "- Current mapped: 29" in requirements_text
    assert "- Current complete: 29" in requirements_text
    assert "- Current pending: 0" in requirements_text

    assert "## v1.3 Closeout & Post-closeout Continuation" in project_text
    assert "`Phase 32` — truth convergence, gate honesty, and quality-10 closeout" in project_text
    _assert_state_keeps_forward_progress_commands(state_text)


def test_phase_33_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "33-contract-truth-unification-hotspot-slimming-and-productization-hardening",
        "33-SUMMARY.md",
        "33-VERIFICATION.md",
    )

    assert "### Phase 33: Contract-truth unification, hotspot slimming, and productization hardening" in roadmap_text
    assert (
        "**Requirements**: [ARC-03, CTRL-07, HOT-08, ERR-07, TST-05, QLT-06, GOV-27, GOV-28, QLT-07]"
        in roadmap_text
    )
    assert "**Status**: Complete (`2026-03-18`)" in roadmap_text
    assert "**Plans**: 6/6 complete" in roadmap_text

    for needle in (
        "- [x] **ARC-03**",
        "- [x] **CTRL-07**",
        "- [x] **HOT-08**",
        "- [x] **ERR-07**",
        "- [x] **TST-05**",
        "- [x] **QLT-06**",
        "- [x] **GOV-27**",
        "- [x] **GOV-28**",
        "- [x] **QLT-07**",
        "| ARC-03 | Phase 33 | Complete |",
        "| CTRL-07 | Phase 33 | Complete |",
        "| HOT-08 | Phase 33 | Complete |",
        "| ERR-07 | Phase 33 | Complete |",
        "| TST-05 | Phase 33 | Complete |",
        "| QLT-06 | Phase 33 | Complete |",
        "| GOV-27 | Phase 33 | Complete |",
        "| GOV-28 | Phase 33 | Complete |",
        "| QLT-07 | Phase 33 | Complete |",
    ):
        assert needle in requirements_text

    assert "## Phase 33 Audit-Driven Continuation" in project_text
    assert "**Execution promise:**" in project_text
    _assert_state_keeps_forward_progress_commands(state_text)


def test_phase_34_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "34-continuity-and-hard-release-gates",
        "34-SUMMARY.md",
        "34-VERIFICATION.md",
    )

    assert "### Phase 34: Continuity and hard release gates" in roadmap_text
    assert "**Requirements**: [GOV-29, QLT-08]" in roadmap_text
    assert "**Status**: Complete (`2026-03-18`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "- [x] 34-01: formalize continuity, custody, and freeze-escalation contracts" in roadmap_text
    assert "- [x] 34-02: add artifact signing and hard release-trust gates" in roadmap_text
    assert "- [x] 34-03: converge public docs, runbook, CODEOWNERS, and guards on continuity/release truth" in roadmap_text

    for needle in (
        "- [x] **GOV-29**",
        "- [x] **QLT-08**",
        "| GOV-29 | Phase 34 | Complete |",
        "| QLT-08 | Phase 34 | Complete |",
    ):
        assert needle in requirements_text

    assert "## Phase 34 Seed Hardening Update" in project_text
    _assert_state_keeps_forward_progress_commands(state_text)


def test_phase_35_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    _assert_promoted_phase_assets(
        "35-protocol-hotspot-final-slimming",
        "35-01-SUMMARY.md",
        "35-02-SUMMARY.md",
        "35-03-SUMMARY.md",
        "35-SUMMARY.md",
        "35-VERIFICATION.md",
    )

    assert "### Phase 35: Protocol hotspot final slimming" in roadmap_text
    assert "**Requirements**: [HOT-09, RES-07]" in roadmap_text
    assert "**Status**: Complete (`2026-03-18`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "| HOT-09 | Phase 35 | Complete |" in requirements_text
    assert "| RES-07 | Phase 35 | Complete |" in requirements_text
    assert "## Phase 35 Protocol Hotspot Slimming Update" in project_text
    assert "## Recommended Next Command" in state_text


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



def test_v1_8_closeout_and_v1_9_current_milestone_truth_are_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    assert "## v1.8: Operational Continuity Automation, Formal-Root Sustainment & Hotspot Round 2" in roadmap_text
    assert "**Milestone status:** `Phase 51 -> 55 complete (2026-03-21)`" in roadmap_text
    assert "**Default next command:** `$gsd-progress`" in roadmap_text
    assert "### Phase 55: Mega-test topicization round 2 and repo-wide typing-metric stratification" in roadmap_text

    for needle in (
        "- [x] **GOV-38**",
        "- [x] **GOV-39**",
        "- [x] **QLT-18**",
        "- [x] **ARC-08**",
        "- [x] **HOT-12**",
        "- [x] **HOT-13**",
        "- [x] **TST-10**",
        "- [x] **TYP-13**",
        "| GOV-38 | Phase 51 | Complete |",
        "| TYP-13 | Phase 55 | Complete |",
        "- v1.8 routed requirements: 8 total",
    ):
        assert needle in requirements_text

    assert "## v1.9: Shared Backoff Neutralization & Cross-Plane Retry Hygiene" in roadmap_text
    assert "**Milestone status:** `Phase 56 complete (2026-03-22)`" in roadmap_text
    assert "**Default next command:** `$gsd-complete-milestone v1.9`" in roadmap_text
    assert "### Phase 56: Shared backoff neutralization and cross-plane retry hygiene" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "**Promoted closeout package**: `56-SUMMARY.md`, `56-VERIFICATION.md`" in roadmap_text

    for needle in (
        "- [x] **RES-13**",
        "- [x] **ARC-09**",
        "- [x] **GOV-40**",
        "| RES-13 | Phase 56 | Complete |",
        "| ARC-09 | Phase 56 | Complete |",
        "| GOV-40 | Phase 56 | Complete |",
        "- v1.9 routed requirements: 3 total",
        "- Current mapped: 3",
        "- Current complete: 3",
        "- Current pending: 0",
    ):
        assert needle in requirements_text

    assert "## Planned Milestone (v1.8)" in project_text
    assert "## Planned Milestone (v1.9)" in project_text
    assert "**Current status:** `Phase 56 complete (2026-03-22)`" in project_text
    assert ".planning/reviews/V1_9_MILESTONE_SEED.md" in project_text
    assert ".planning/phases/56-shared-backoff-neutralization-and-cross-plane-retry-hygiene/56-01-PLAN.md" in project_text
    assert ".planning/phases/56-shared-backoff-neutralization-and-cross-plane-retry-hygiene/56-SUMMARY.md" in project_text
    assert "$gsd-complete-milestone v1.9" in project_text

    assert "## v1.10: Command-Result Typed Outcome & Reason-Code Hardening" in roadmap_text
    assert "**Milestone status:** `Phase 57 complete (2026-03-22)`" in roadmap_text
    assert "**Default next command:** `$gsd-complete-milestone v1.10`" in roadmap_text
    assert "### Phase 57: Command-result typed outcome and reason-code hardening" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "**Promoted closeout package**: `57-SUMMARY.md`, `57-VERIFICATION.md`" in roadmap_text

    for needle in (
        "- [x] **ERR-12**",
        "- [x] **TYP-14**",
        "- [x] **GOV-41**",
        "| ERR-12 | Phase 57 | Complete |",
        "| TYP-14 | Phase 57 | Complete |",
        "| GOV-41 | Phase 57 | Complete |",
        "- v1.10 routed requirements: 3 total",
        "- Current mapped: 3",
        "- Current complete: 3",
        "- Current pending: 0",
    ):
        assert needle in requirements_text

    assert "## Planned Milestone (v1.10)" in project_text
    assert "**Current status:** `Phase 57 complete (2026-03-22)`" in project_text
    assert ".planning/reviews/V1_10_MILESTONE_SEED.md" in project_text
    assert ".planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-01-PLAN.md" in project_text
    assert ".planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-SUMMARY.md" in project_text
    assert "$gsd-complete-milestone v1.10" in project_text

    assert "## v1.11: Repository Audit Refresh & Next-Wave Remediation Routing" in roadmap_text
    assert "**Milestone status:** `Phase 58 complete (2026-03-22)`" in roadmap_text
    assert "**Default next command:** `$gsd-complete-milestone v1.11`" in roadmap_text
    assert "### Phase 58: Repository audit refresh and next-wave routing" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "**Promoted closeout package**: `58-SUMMARY.md`, `58-VERIFICATION.md`" in roadmap_text

    for needle in (
        "- [x] **AUD-03**",
        "- [x] **ARC-10**",
        "- [x] **OSS-06**",
        "- [x] **GOV-42**",
        "| AUD-03 | Phase 58 | Complete |",
        "| ARC-10 | Phase 58 | Complete |",
        "| OSS-06 | Phase 58 | Complete |",
        "| GOV-42 | Phase 58 | Complete |",
        "- v1.11 routed requirements: 4 total",
        "- Current mapped: 4",
        "- Current complete: 4",
        "- Current pending: 0",
    ):
        assert needle in requirements_text

    assert "## Planned Milestone (v1.11)" in project_text
    assert "**Current status:** `Phase 58 complete (2026-03-22)`" in project_text
    assert ".planning/reviews/V1_11_MILESTONE_SEED.md" in project_text
    assert ".planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-01-PLAN.md" in project_text
    assert ".planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-SUMMARY.md" in project_text
    assert "$gsd-complete-milestone v1.11" in project_text

    assert "**Current milestone:** `v1.11 Repository Audit Refresh & Next-Wave Remediation Routing`" in state_text
    assert "**Current mode:** `Phase 58 complete`" in state_text
    assert "$gsd-complete-milestone v1.11" in state_text
    assert ".planning/reviews/V1_11_MILESTONE_SEED.md" in state_text
