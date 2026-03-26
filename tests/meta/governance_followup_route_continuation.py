"""Governance guards for continuity routing and archived-milestone follow-up truth."""

from __future__ import annotations

from .governance_contract_helpers import (
    _ROOT,
    _assert_state_keeps_forward_progress_commands,
)
from .governance_promoted_assets import (
    _assert_phase_assets_not_promoted,
    _assert_promoted_phase_assets,
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
