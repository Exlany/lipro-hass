"""Current-route and archived-baseline follow-up truth guards spanning v1.8-v1.21."""

from __future__ import annotations

from .conftest import _ROOT
from .governance_contract_helpers import _assert_latest_archived_route_truth
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_STATE_LABEL,
    CURRENT_MILESTONE_STATUS,
    CURRENT_ROUTE_MODE,
    HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH,
    HISTORICAL_CLOSEOUT_ROUTE_TRUTH,
    LATEST_ARCHIVED_AUDIT_PATH,
    LATEST_ARCHIVED_EVIDENCE_PATH,
    assert_machine_readable_route_contracts,
)
from .governance_promoted_assets import _assert_promoted_closeout_package


def test_archived_route_followup_truth_from_v1_8_to_v1_20_is_consistent() -> None:
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(
        encoding="utf-8"
    )
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
    _assert_promoted_closeout_package(roadmap_text, "56-SUMMARY.md", "56-VERIFICATION.md")

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
    _assert_promoted_closeout_package(roadmap_text, "57-SUMMARY.md", "57-VERIFICATION.md")

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
    _assert_promoted_closeout_package(roadmap_text, "58-SUMMARY.md", "58-VERIFICATION.md")

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
    _assert_promoted_closeout_package(roadmap_text, "59-SUMMARY.md", "59-VERIFICATION.md")

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

    contracts = assert_machine_readable_route_contracts()
    assert contracts["REQUIREMENTS"]["active_milestone"]["phase"] == "79"
    assert contracts["MILESTONES"]["latest_archived"]["version"] == "v1.20"
    assert (
        contracts["STATE"]["bootstrap"]["latest_archived_evidence_pointer"]
        == LATEST_ARCHIVED_EVIDENCE_PATH
    )
    assert HISTORICAL_CLOSEOUT_ROUTE_TRUTH in milestones_text
    assert HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH in milestones_text
    assert HISTORICAL_CLOSEOUT_ROUTE_TRUTH in requirements_text
    assert HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH in requirements_text
    assert HISTORICAL_CLOSEOUT_ROUTE_TRUTH in roadmap_text
    assert HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH in roadmap_text

    for text in (milestones_text, roadmap_text, requirements_text):
        assert "current governance state =" not in text
        assert "当前治理状态已切换为" not in text
        assert "当前治理状态现已切换为" not in text
        assert "live governance state" not in text

    _assert_latest_archived_route_truth(project_text, roadmap_text, state_text)
    assert "## Current Milestone (v1.21)" in project_text
    assert "## Archived Milestone (v1.17)" in project_text
    assert "## Archived Milestone (v1.16)" in project_text
    assert "**Current status:** `archived / evidence-ready with carry-forward (2026-03-24)`" in project_text
    assert "## Archived Milestone (v1.15)" in project_text

    assert "Plans:" in roadmap_text
    assert "75-04: promote v1.20 closeout evidence and freeze the Phase 75 governance truth" in roadmap_text
    assert "### Phase 69: Residual read-model closure, wrapper-path thinning, and quality-balance follow-through" in roadmap_text

    for needle in (
        "- [x] **GOV-56**",
        "- [x] **ARC-19**",
        "- [x] **HOT-32**",
        "- [x] **HOT-33**",
        "- [x] **HOT-34**",
        "- [x] **TYP-21**",
        "- [x] **TST-22**",
        "- [x] **QLT-30**",
        "| GOV-56 | Phase 72, 74, 75 | Completed |",
        "| ARC-19 | Phase 72, 73, 75 | Completed |",
        "| HOT-32 | Phase 72 | Completed |",
        "| HOT-33 | Phase 73 | Completed |",
        "| HOT-34 | Phase 74 | Completed |",
        "| TYP-21 | Phase 72, 73, 75 | Completed |",
        "| TST-22 | Phase 72, 73, 74, 75 | Completed |",
        "| QLT-30 | Phase 72, 73, 74, 75 | Completed |",
        "- v1.20 routed requirements: 8 total",
        "- Current mapped: 8",
        "- Current complete: 8",
        "- Current pending: 0",
        "## Previous Archived Milestone (v1.19)",
        "## Traceability for archived v1.16 route",
        "| GOV-52 | Phase 68 | Completed |",
        "| QLT-26 | Phase 68 | Completed |",
    ):
        assert needle in requirements_text

    assert f"**Current milestone:** `{CURRENT_MILESTONE_STATE_LABEL}`" in state_text
    assert f"**Current mode:** `{CURRENT_ROUTE_MODE}`" in state_text
    assert "closeout-ready" in CURRENT_MILESTONE_STATUS
    assert CURRENT_MILESTONE_DEFAULT_NEXT in state_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in roadmap_text
    assert LATEST_ARCHIVED_AUDIT_PATH in state_text
    assert LATEST_ARCHIVED_EVIDENCE_PATH in state_text
