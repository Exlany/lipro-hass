"""Governance guards for milestone closeout, archive snapshots, and handoff truth."""

from __future__ import annotations

from functools import lru_cache
import re
from pathlib import Path

from scripts.check_file_matrix import repo_root

from .test_governance_guards import _load_frontmatter


def _assert_state_keeps_forward_progress_commands(state_text: str) -> None:
    assert "## Recommended Next Command" in state_text
    assert "$gsd-progress" in state_text
    assert (
        "$gsd-plan-milestone-gaps" in state_text
        or "$gsd-new-milestone" in state_text
        or re.search(r"\$gsd-(?:plan|execute)-phase \d+(?:\.\d+)?", state_text)
        or re.search(r"\$gsd-complete-milestone v\d+\.\d+", state_text)
    )


def _assert_project_allows_post_v1_4_next_step(project_text: str) -> None:
    assert (
        "**Default next step:** `$gsd-new-milestone`" in project_text
        or re.search(
            r"\*\*Default next step:\*\* `\$gsd-plan-phase \d+(?:\.\d+)?` → `\$gsd-execute-phase \d+(?:\.\d+)?`",
            project_text,
        )
        is not None
    )


def _assert_state_reflects_post_v1_4_continuation(state_text: str) -> None:
    assert (
        "`Phase 39 complete`" in state_text
        or re.search(r"Phase \d+(?:\.\d+)? (?:execution-ready|complete|routing-ready|planning-ready)", state_text)
        or re.search(r"v1\.\d+ archived", state_text)
        or re.search(r"\$gsd-(?:plan|execute)-phase \d+(?:\.\d+)?", state_text)
        or re.search(r"\$gsd-complete-milestone v\d+\.\d+", state_text)
        or "$gsd-new-milestone" in state_text
    )

_ROOT = repo_root(Path(__file__))

_PROMOTED_PHASE_ASSETS = _ROOT / ".planning" / "reviews" / "PROMOTED_PHASE_ASSETS.md"


@lru_cache(maxsize=1)
def _load_promoted_phase_assets() -> dict[str, frozenset[str]]:
    manifest = _load_frontmatter(_PROMOTED_PHASE_ASSETS)
    phases = manifest["phases"]
    assert isinstance(phases, dict)

    promoted_assets: dict[str, frozenset[str]] = {}
    for phase_dir_name, filenames in phases.items():
        assert isinstance(phase_dir_name, str)
        assert isinstance(filenames, list)
        assert filenames
        promoted_assets[phase_dir_name] = frozenset(filenames)

    return promoted_assets


def _assert_promoted_phase_assets(phase_dir_name: str, *filenames: str) -> None:
    promoted_assets = _load_promoted_phase_assets()
    assert phase_dir_name in promoted_assets

    phase_root = _ROOT / ".planning" / "phases" / phase_dir_name
    for filename in filenames:
        assert filename in promoted_assets[phase_dir_name]
        assert (phase_root / filename).exists()


def _assert_phase_assets_not_promoted(phase_dir_name: str, *filenames: str) -> None:
    promoted_assets = _load_promoted_phase_assets().get(phase_dir_name, frozenset())

    for filename in filenames:
        assert filename not in promoted_assets


def test_promoted_phase_assets_manifest_enforces_explicit_ci_evidence() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    manifest = _load_frontmatter(_PROMOTED_PHASE_ASSETS)
    policy = manifest["policy"]

    assert isinstance(policy, dict)
    assert policy["default_identity"] == "execution-trace"
    assert ".planning/ROADMAP.md" in policy["promotion_sources"]
    assert ".planning/baseline/VERIFICATION_MATRIX.md" in policy["promotion_sources"]
    assert ".planning/milestones/*.md" in policy["promotion_sources"]
    assert ".planning/reviews/*.md" in policy["promotion_sources"]
    assert ".planning/reviews/PROMOTED_PHASE_ASSETS.md" in roadmap_text
    assert ".planning/reviews/PROMOTED_PHASE_ASSETS.md" in state_text

    for phase_dir_name, filenames in _load_promoted_phase_assets().items():
        for filename in filenames:
            assert not filename.endswith(
                (
                    "-PLAN.md",
                    "-CONTEXT.md",
                    "-RESEARCH.md",
                    "-PRD.md",
                    "-ARCHITECTURE.md",
                    "-UAT.md",
                )
            )
            assert (
                _ROOT / ".planning" / "phases" / phase_dir_name / filename
            ).exists()

    _assert_phase_assets_not_promoted(
        "15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through",
        "15-CONTEXT.md",
        "15-01-PLAN.md",
    )
    _assert_phase_assets_not_promoted(
        "24-final-milestone-audit-archive-readiness-and-v1-3-handoff-prep",
        "24-CONTEXT.md",
        "24-03-PLAN.md",
    )
    _assert_phase_assets_not_promoted(
        "30-protocol-control-typed-contract-tightening",
        "30-VALIDATION.md",
        "30-01-SUMMARY.md",
    )
    _assert_phase_assets_not_promoted(
        "32-truth-convergence-gate-honesty-and-quality-10-closeout",
        "32-CONTEXT.md",
        "32-RESEARCH.md",
        "32-01-PLAN.md",
        "32-VALIDATION.md",
    )
    _assert_phase_assets_not_promoted(
        "34-continuity-and-hard-release-gates",
        "34-01-PLAN.md",
        "34-VALIDATION.md",
    )
    _assert_phase_assets_not_promoted(
        "39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition",
        "39-PRD.md",
        "39-CONTEXT.md",
        "39-01-PLAN.md",
        "39-02-PLAN.md",
        "39-03-PLAN.md",
        "39-04-PLAN.md",
        "39-05-PLAN.md",
        "39-06-PLAN.md",
        "39-VALIDATION.md",
    )
    _assert_phase_assets_not_promoted(
        "40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification",
        "40-CONTEXT.md",
        "40-01-PLAN.md",
        "40-02-PLAN.md",
        "40-03-PLAN.md",
        "40-04-PLAN.md",
        "40-05-PLAN.md",
        "40-06-PLAN.md",
        "40-07-PLAN.md",
        "40-VALIDATION.md",
    )


def test_v1_1_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_1_EVIDENCE_INDEX.md"

    assert evidence_index.exists()
    _assert_promoted_phase_assets(
        "07.5-integration-governance-verification-closeout",
        "07.5-SUMMARY.md",
        "07.5-01-SUMMARY.md",
        "07.5-02-SUMMARY.md",
        "07.5-VERIFICATION.md",
    )

    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    assert "07.3-runtime-telemetry-exporter" in evidence_text
    assert "07.4-protocol-replay-simulator-harness" in evidence_text
    assert "Phase 8 Pull Boundary" in evidence_text

def test_governance_truth_registers_v1_1_closeout_assets() -> None:
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "runtime telemetry exporter family" in authority_text
    assert "v1.1 closeout evidence index" in authority_text
    assert "7 / 7.5 / 15 / 16 / 17" in verification_text
    assert "V1_1_EVIDENCE_INDEX.md" in authority_text
    assert "## Phase 07.5 Residual Delta" in residual_text
    assert "de-scope" in residual_text
    assert "## Phase 07.5 Status Update" in kill_text

def test_v1_2_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_2_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.2-MILESTONE-AUDIT.md"
    handoff = _ROOT / ".planning" / "v1.3-HANDOFF.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert handoff.exists()
    _assert_promoted_phase_assets(
        "23-governance-convergence-contributor-docs-and-release-evidence-closure",
        "23-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "24-final-milestone-audit-archive-readiness-and-v1-3-handoff-prep",
        "24-VERIFICATION.md",
    )

    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    assert "21-VERIFICATION.md" in evidence_text
    assert "24-VERIFICATION.md" in evidence_text
    assert "archive-ready" in evidence_text
    assert "handoff-ready" in evidence_text

def test_governance_truth_registers_v1_2_closeout_assets() -> None:
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(
        encoding="utf-8"
    )

    assert "V1_2_EVIDENCE_INDEX.md" in authority_text
    assert "## Phase 21 Replay / Exception Taxonomy Contract" in verification_text
    assert "## Phase 24 Final Audit / Archive-Ready / Handoff Contract" in verification_text
    assert "## Phase 24 Final Audit Disposition" in residual_text
    assert "## Phase 24 Status Update" in kill_text
    assert "## v1.2 Host-Neutral Core & Replay Completion" in milestones_text

def test_milestone_archive_snapshots_exist_and_are_referenced() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(encoding="utf-8")

    archive_paths = (
        _ROOT / ".planning" / "milestones" / "v1.1-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.1-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.2-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.2-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.4-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.4-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.5-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.5-REQUIREMENTS.md",
    )

    for path in archive_paths:
        assert path.exists()

    for needle in (
        "v1.1-ROADMAP.md",
        "v1.1-REQUIREMENTS.md",
        "v1.2-ROADMAP.md",
        "v1.2-REQUIREMENTS.md",
        "v1.4-ROADMAP.md",
        "v1.4-REQUIREMENTS.md",
        "v1.5-ROADMAP.md",
        "v1.5-REQUIREMENTS.md",
    ):
        assert needle in roadmap_text
        assert needle in requirements_text or needle in project_text or needle in milestones_text

    assert "archive snapshots 已落入 `.planning/milestones/`" in state_text
    assert "archived / evidence-ready" in milestones_text
    assert "archived snapshots created / handoff-ready" in milestones_text
    assert "revalidated 2026-03-17" in milestones_text
    assert ".planning/v1.4-MILESTONE-AUDIT.md" in milestones_text
    assert ".planning/v1.5-MILESTONE-AUDIT.md" in milestones_text
    assert "V1_4_EVIDENCE_INDEX.md" in milestones_text
    assert "V1_5_EVIDENCE_INDEX.md" in milestones_text
    assert ".planning/v1.5-MILESTONE-AUDIT.md" in milestones_text
    assert "V1_5_EVIDENCE_INDEX.md" in milestones_text

    v1_1_archive_text = (
        _ROOT / ".planning" / "milestones" / "v1.1-ROADMAP.md"
    ).read_text(encoding="utf-8")

    assert "待执行 milestone archival" not in v1_1_archive_text
    assert "当当前里程碑完成时，应能同时回答以下问题：" in project_text


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
        ("### Phase 28: Release trust gate completion and maintainer resilience", "### Phase 29:", "3/3 complete"),
        ("### Phase 29: REST child-façade slimming and test topicization", "### Phase 30:", "3/3 complete"),
        ("### Phase 30: Protocol/control typed contract tightening", "### Phase 31:", "3/3 complete"),
        ("### Phase 31: Runtime/service typed budget and exception closure", None, "4/4 complete"),
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
    assert "| _None_ | — | — | — | Phase 38 已关闭最后一条已登记 residual family。 |" in residual_text
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


def test_v1_5_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_5_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.5-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.5-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.5-REQUIREMENTS.md").exists()
    assert (_ROOT / ".planning" / "phases" / "40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification" / "40-VALIDATION.md").exists()
    _assert_promoted_phase_assets(
        "40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification",
        "40-SUMMARY.md",
        "40-VERIFICATION.md",
    )

    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    assert "40-VERIFICATION.md" in evidence_text
    assert "archive-ready / shipped" in evidence_text
    assert "V1_5_EVIDENCE_INDEX.md" in evidence_text


def test_governance_truth_registers_v1_5_closeout_assets() -> None:
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    public_text = (
        _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
    ).read_text(encoding="utf-8")
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(encoding="utf-8")

    assert "V1_5_EVIDENCE_INDEX.md" in authority_text
    assert "v1.5-MILESTONE-AUDIT.md" in authority_text
    assert "V1_5_EVIDENCE_INDEX.md" in public_text
    assert "## v1.5 Governance Truth Consolidation & Control-Surface Finalization" in milestones_text


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
