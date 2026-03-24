"""Current milestone follow-up routing truth guards."""

from __future__ import annotations

from .test_governance_closeout_guards import _ROOT


def test_v1_8_closeout_through_v1_15_archived_truth_are_consistent() -> None:
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
        "- Current complete: 9",
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
        "- Current complete: 9",
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
    assert "**Archive status:** `archived / evidence-ready (2026-03-22)`" in roadmap_text
    assert ".planning/v1.12-MILESTONE-AUDIT.md" in roadmap_text
    assert ".planning/reviews/V1_12_EVIDENCE_INDEX.md" in roadmap_text
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
        "- Current complete: 9",
        "- Current pending: 0",
    ):
        assert needle in requirements_text

    assert "## v1.13: Tooling Truth Decomposition, Formal-Home Slimming & Naming/Discoverability Convergence" in roadmap_text
    assert "**Archive status:** `archived / evidence-ready (2026-03-22)`" in roadmap_text
    assert ".planning/v1.13-MILESTONE-AUDIT.md" in roadmap_text
    assert ".planning/reviews/V1_15_EVIDENCE_INDEX.md" in roadmap_text
    assert ".planning/milestones/v1.13-ROADMAP.md" in roadmap_text
    assert ".planning/milestones/v1.13-REQUIREMENTS.md" in roadmap_text
    assert "### Phase 60: Tooling truth decomposition and file-governance maintainability" in roadmap_text
    assert "**Plans**: 3 completed" in roadmap_text
    assert "60-01: decompose the file-matrix checker into thin root and internal truth families" in roadmap_text
    assert "60-02: topicize toolchain truth guards by stable concern family" in roadmap_text
    assert "60-03: freeze tooling topology in governance truth and focused guards" in roadmap_text

    for needle in (
        "- [x] **HOT-14**",
        "- [x] **TST-12**",
        "- [x] **GOV-44**",
        "- v1.13 routed requirements: 9 total",
        "- Current mapped: 9",
        "- Current complete: 9",
        "- Current pending: 0",
    ):
        assert needle in requirements_text

    assert "## Archived Milestone (v1.13)" in project_text
    assert "**Current status:** `archived / evidence-ready (2026-03-22)`" in project_text
    assert ".planning/v1.13-MILESTONE-AUDIT.md" in project_text
    assert ".planning/reviews/V1_15_EVIDENCE_INDEX.md" in project_text
    assert ".planning/milestones/v1.13-ROADMAP.md" in project_text
    assert ".planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-01-PLAN.md" not in project_text

    assert "**Status:** Active milestone route = `v1.18 / Phase 70`; latest archived closeout pointer = `.planning/reviews/V1_17_EVIDENCE_INDEX.md`." in project_text
    assert "## Current Milestone (v1.18)" in project_text
    assert "**Current status:** `active / Phase 70 complete / closeout-ready (2026-03-24)`" in project_text
    assert "**Default next command:** `$gsd-next`" in project_text
    assert "## Latest Archived Milestone (v1.17)" in project_text
    assert "## Archived Milestone (v1.16)" in project_text
    assert "**Current status:** `archived / evidence-ready with carry-forward (2026-03-24)`" in project_text
    assert "## Archived Milestone (v1.15)" in project_text

    assert "### 🟢 v1.18: Support-Seam Slimming, OTA Resolver Consolidation & Governance Test Topicization" in roadmap_text
    assert "**Current Status:** `Phase 70` complete / closeout-ready（2026-03-24）；默认下一步是 `$gsd-next`。" in roadmap_text
    assert "### Phase 70: Support-seam slimming, OTA resolver consolidation, and governance test topicization" in roadmap_text
    assert "Plans:" in roadmap_text
    assert "70-05: sync planning-baseline truths and run the final phase gate" in roadmap_text
    assert "### Phase 69: Residual read-model closure, wrapper-path thinning, and quality-balance follow-through" in roadmap_text

    for needle in (
        "- [x] **GOV-54**",
        "- [x] **ARC-17**",
        "- [x] **HOT-28**",
        "- [x] **HOT-29**",
        "- [x] **OSS-10**",
        "- [x] **TST-20**",
        "- [x] **QLT-28**",
        "| GOV-54 | Phase 70 | Completed |",
        "| ARC-17 | Phase 70 | Completed |",
        "| HOT-28 | Phase 70 | Completed |",
        "| HOT-29 | Phase 70 | Completed |",
        "| OSS-10 | Phase 70 | Completed |",
        "| TST-20 | Phase 70 | Completed |",
        "| QLT-28 | Phase 70 | Completed |",
        "- v1.18 routed requirements: 7 total",
        "- Current mapped: 7",
        "- Current complete: 7",
        "- Current pending: 0",
        "## Traceability for archived v1.16 route",
        "| GOV-52 | Phase 68 | Completed |",
        "| QLT-26 | Phase 68 | Completed |",
    ):
        assert needle in requirements_text

    assert "**Current milestone:** `v1.18 Support-Seam Slimming, OTA Resolver Consolidation & Governance Test Topicization`" in state_text
    assert "**Current mode:** `v1.18 active / Phase 70 complete / closeout-ready`" in state_text
    assert "$gsd-next" in state_text
    assert ".planning/v1.17-MILESTONE-AUDIT.md" in state_text
    assert ".planning/reviews/V1_17_EVIDENCE_INDEX.md" in state_text
