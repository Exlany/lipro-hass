"""Current milestone follow-up routing truth guards."""

from __future__ import annotations

from .test_governance_closeout_guards import _ROOT


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

    assert "## v1.12: Verification Localization & Governance Guard Topicization" in roadmap_text
    assert "**Milestone status:** `Phase 59 complete (2026-03-22)`" in roadmap_text
    assert "**Default next command:** `$gsd-complete-milestone v1.12`" in roadmap_text
    assert "### Phase 59: Verification localization and governance guard topicization" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "**Promoted closeout package**: `59-SUMMARY.md`, `59-VERIFICATION.md`" in roadmap_text

    for needle in (
        "- [x] **TST-11**",
        "- [x] **QLT-19**",
        "- [x] **GOV-43**",
        "| TST-11 | Phase 59 | Complete |",
        "| QLT-19 | Phase 59 | Complete |",
        "| GOV-43 | Phase 59 | Complete |",
        "- v1.12 routed requirements: 3 total",
        "- Current mapped: 3",
        "- Current complete: 3",
        "- Current pending: 0",
    ):
        assert needle in requirements_text

    assert "## Planned Milestone (v1.11)" in project_text
    assert "**Current status:** `Phase 58 complete (2026-03-22)`" in project_text
    assert ".planning/reviews/V1_11_MILESTONE_SEED.md" in project_text
    assert ".planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-01-PLAN.md" in project_text
    assert ".planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-SUMMARY.md" in project_text
    assert "$gsd-complete-milestone v1.11" in project_text

    assert "## Planned Milestone (v1.12)" in project_text
    assert "**Current status:** `Phase 59 complete (2026-03-22)`" in project_text
    assert ".planning/reviews/V1_12_MILESTONE_SEED.md" in project_text
    assert ".planning/phases/59-verification-localization-and-governance-guard-topicization/59-SUMMARY.md" in project_text
    assert ".planning/phases/59-verification-localization-and-governance-guard-topicization/59-VERIFICATION.md" in project_text
    assert "$gsd-complete-milestone v1.12" in project_text

    assert "**Current milestone:** `v1.12 Verification Localization & Governance Guard Topicization`" in state_text
    assert "**Current mode:** `Phase 59 complete`" in state_text
    assert "$gsd-complete-milestone v1.12" in state_text
    assert ".planning/reviews/V1_12_MILESTONE_SEED.md" in state_text
