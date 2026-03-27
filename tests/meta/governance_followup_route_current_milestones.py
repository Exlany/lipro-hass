"""Current-route and archived-baseline follow-up truth guards spanning v1.8-v1.23."""

from __future__ import annotations

from .conftest import _ROOT, _as_mapping
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
    _as_optional_mapping,
    assert_machine_readable_route_contracts,
)
from .governance_promoted_assets import _assert_promoted_closeout_package

_MILESTONES_TEXT = (_ROOT / ".planning" / "MILESTONES.md").read_text(encoding="utf-8")
_ROADMAP_TEXT = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
_REQUIREMENTS_TEXT = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
_PROJECT_TEXT = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
_STATE_TEXT = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")


def _assert_contains_all(text: str, *needles: str) -> None:
    for needle in needles:
        assert needle in text


def _assert_not_contains_any(text: str, *needles: str) -> None:
    for needle in needles:
        assert needle not in text


def test_v1_8_followup_route_truth_is_recorded_in_roadmap_and_requirements() -> None:
    _assert_contains_all(
        _ROADMAP_TEXT,
        "## v1.8: Operational Continuity Automation, Formal-Root Sustainment & Hotspot Round 2",
        "**Milestone status:** `Phase 51 -> 55 complete (2026-03-21)`",
        "**Default next command:** `$gsd-progress`",
        "### Phase 55: Mega-test topicization round 2 and repo-wide typing-metric stratification",
    )
    _assert_contains_all(
        _REQUIREMENTS_TEXT,
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
    )


def test_v1_9_closeout_package_and_project_pointers_are_consistent() -> None:
    _assert_contains_all(
        _ROADMAP_TEXT,
        "## v1.9: Shared Backoff Neutralization & Cross-Plane Retry Hygiene",
        "**Milestone status:** `Phase 56 complete (2026-03-22)`",
        "**Default next command:** `$gsd-complete-milestone v1.9`",
        "### Phase 56: Shared backoff neutralization and cross-plane retry hygiene",
        "**Plans**: 3/3 complete",
    )
    _assert_promoted_closeout_package(_ROADMAP_TEXT, "56-SUMMARY.md", "56-VERIFICATION.md")
    _assert_contains_all(
        _REQUIREMENTS_TEXT,
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
    )
    _assert_contains_all(
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
    _assert_contains_all(
        _ROADMAP_TEXT,
        "## v1.10: Command-Result Typed Outcome & Reason-Code Hardening",
        "**Milestone status:** `Phase 57 complete (2026-03-22)`",
        "**Default next command:** `$gsd-complete-milestone v1.10`",
        "### Phase 57: Command-result typed outcome and reason-code hardening",
        "**Plans**: 3/3 complete",
    )
    _assert_promoted_closeout_package(_ROADMAP_TEXT, "57-SUMMARY.md", "57-VERIFICATION.md")
    _assert_contains_all(
        _REQUIREMENTS_TEXT,
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
    )
    _assert_contains_all(
        _PROJECT_TEXT,
        "## Planned Milestone (v1.10)",
        "**Current status:** `Phase 57 complete (2026-03-22)`",
        ".planning/reviews/V1_10_MILESTONE_SEED.md",
        ".planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-01-PLAN.md",
        ".planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-SUMMARY.md",
        "$gsd-complete-milestone v1.10",
    )


def test_v1_11_closeout_package_and_project_pointers_are_consistent() -> None:
    _assert_contains_all(
        _ROADMAP_TEXT,
        "## v1.11: Repository Audit Refresh & Next-Wave Remediation Routing",
        "**Milestone status:** `Phase 58 complete (2026-03-22)`",
        "**Default next command:** `$gsd-complete-milestone v1.11`",
        "### Phase 58: Repository audit refresh and next-wave routing",
        "**Plans**: 3/3 complete",
    )
    _assert_promoted_closeout_package(_ROADMAP_TEXT, "58-SUMMARY.md", "58-VERIFICATION.md")
    _assert_contains_all(
        _REQUIREMENTS_TEXT,
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
        "- Current complete: 8",
        "- Current pending: 0",
    )


def test_v1_12_to_v1_13_archived_route_truth_uses_promoted_evidence_only() -> None:
    _assert_contains_all(
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
    _assert_contains_all(
        _REQUIREMENTS_TEXT,
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
        "- [x] **HOT-14**",
        "- [x] **TST-12**",
        "- [x] **GOV-44**",
        "- v1.13 routed requirements: 9 total",
        "- Current mapped: 9",
        "- Current complete: 9",
        "- Current pending: 0",
    )
    _assert_contains_all(
        _PROJECT_TEXT,
        "## Archived Milestone (v1.13)",
        "**Current status:** `archived / evidence-ready (2026-03-22)`",
        ".planning/v1.13-MILESTONE-AUDIT.md",
        ".planning/reviews/V1_15_EVIDENCE_INDEX.md",
        ".planning/milestones/v1.13-ROADMAP.md",
    )
    assert ".planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-01-PLAN.md" not in _PROJECT_TEXT


def test_machine_readable_route_contracts_point_to_archived_v1_23_and_previous_baselines() -> None:
    contracts = assert_machine_readable_route_contracts()
    requirements_contract = _as_mapping(contracts["REQUIREMENTS"])
    requirements_active = _as_optional_mapping(requirements_contract["active_milestone"])
    milestones_contract = _as_mapping(contracts["MILESTONES"])
    milestones_active = _as_optional_mapping(milestones_contract["active_milestone"])
    milestones_latest_archived = _as_mapping(milestones_contract["latest_archived"])
    milestones_previous_archived = _as_mapping(milestones_contract["previous_archived"])
    state_contract = _as_mapping(contracts["STATE"])
    state_bootstrap = _as_mapping(state_contract["bootstrap"])

    assert requirements_active is None
    assert milestones_active is None
    assert milestones_latest_archived["version"] == "v1.23"
    assert milestones_latest_archived["phase"] == "88"
    assert milestones_previous_archived["version"] == "v1.22"
    assert state_bootstrap["default_next_command"] == CURRENT_MILESTONE_DEFAULT_NEXT
    assert state_bootstrap["latest_archived_evidence_pointer"] == LATEST_ARCHIVED_EVIDENCE_PATH


def test_historical_route_truth_replaces_legacy_live_state_wording() -> None:
    for text in (_MILESTONES_TEXT, _ROADMAP_TEXT, _REQUIREMENTS_TEXT):
        _assert_contains_all(
            text,
            HISTORICAL_CLOSEOUT_ROUTE_TRUTH,
            HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH,
        )
        _assert_not_contains_any(
            text,
            "current governance state =",
            "当前治理状态已切换为",
            "当前治理状态现已切换为",
            "live governance state",
        )


def test_current_v1_23_project_state_and_latest_archive_pointers_align() -> None:
    _assert_latest_archived_route_truth(_PROJECT_TEXT, _ROADMAP_TEXT, _STATE_TEXT)
    _assert_contains_all(
        _PROJECT_TEXT,
        "## Latest Archived Milestone (v1.23)",
        "## Previous Archived Milestone (v1.22)",
        "## Archived Milestone (v1.21)",
        "## Archived Milestone (v1.17)",
        "## Archived Milestone (v1.16)",
        "## Archived Milestone (v1.15)",
        "**Current status:** `archived / evidence-ready (2026-03-27)`",
    )
    _assert_contains_all(
        _ROADMAP_TEXT,
        "### Phase 85: Terminal audit refresh and residual routing",
        "### Phase 86: Production residual eradication and boundary re-tightening",
        "### Phase 87: Assurance hotspot decomposition and no-regrowth guards",
        "### Phase 88: Governance sync, quality proof, and milestone freeze",
        CURRENT_MILESTONE_DEFAULT_NEXT,
        ".planning/reviews/V1_23_EVIDENCE_INDEX.md",
        ".planning/milestones/v1.23-ROADMAP.md",
        "### Phase 84: Governance/open-source guard coverage and milestone truth freeze",
    )
    _assert_contains_all(
        _REQUIREMENTS_TEXT,
        "- [x] **AUD-04**",
        "- [x] **GOV-62**",
        "- [x] **HOT-37**",
        "- [x] **ARC-22**",
        "- [x] **HOT-38**",
        "- [x] **TST-27**",
        "- [x] **GOV-63**",
        "- [x] **QLT-35**",
        "| AUD-04 | Phase 85 | Completed |",
        "| GOV-62 | Phase 85 | Completed |",
        "| HOT-37 | Phase 86 | Completed |",
        "| ARC-22 | Phase 86 | Completed |",
        "| HOT-38 | Phase 87 | Completed |",
        "| TST-27 | Phase 87 | Completed |",
        "| GOV-63 | Phase 88 | Completed |",
        "| QLT-35 | Phase 88 | Completed |",
        "- v1.23 routed requirements: 8 total",
        "- Current mapped: 8",
        "- Current complete: 8",
        "- Current pending: 0",
        "## Previous Archived Milestone (v1.22)",
        "## Archived Milestone (v1.21)",
        "## Previous Archived Milestone (v1.20)",
        "## Traceability for archived v1.16 route",
        "| GOV-52 | Phase 68 | Completed |",
        "| QLT-26 | Phase 68 | Completed |",
    )
    _assert_contains_all(
        _STATE_TEXT,
        f"**Current milestone:** `{CURRENT_MILESTONE_STATE_LABEL}`",
        f"**Current mode:** `{CURRENT_ROUTE_MODE}`",
        CURRENT_MILESTONE_DEFAULT_NEXT,
        LATEST_ARCHIVED_AUDIT_PATH,
        LATEST_ARCHIVED_EVIDENCE_PATH,
        ".planning/reviews/V1_23_TERMINAL_AUDIT.md",
    )
    assert CURRENT_MILESTONE_STATUS == "archived / evidence-ready (2026-03-27)"
