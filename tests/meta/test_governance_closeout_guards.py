"""Governance guards for milestone closeout, archive snapshots, and handoff truth."""

from __future__ import annotations

from pathlib import Path

from scripts.check_file_matrix import repo_root

_ROOT = repo_root(Path(__file__))


def test_v1_1_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_1_EVIDENCE_INDEX.md"
    phase_summary = (
        _ROOT
        / ".planning"
        / "phases"
        / "07.5-integration-governance-verification-closeout"
        / "07.5-SUMMARY.md"
    )
    plan_01_summary = (
        _ROOT
        / ".planning"
        / "phases"
        / "07.5-integration-governance-verification-closeout"
        / "07.5-01-SUMMARY.md"
    )
    plan_02_summary = (
        _ROOT
        / ".planning"
        / "phases"
        / "07.5-integration-governance-verification-closeout"
        / "07.5-02-SUMMARY.md"
    )
    verification = (
        _ROOT
        / ".planning"
        / "phases"
        / "07.5-integration-governance-verification-closeout"
        / "07.5-VERIFICATION.md"
    )

    assert evidence_index.exists()
    assert phase_summary.exists()
    assert plan_01_summary.exists()
    assert plan_02_summary.exists()
    assert verification.exists()

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
    phase_23_verification = (
        _ROOT
        / ".planning"
        / "phases"
        / "23-governance-convergence-contributor-docs-and-release-evidence-closure"
        / "23-VERIFICATION.md"
    )
    phase_24_verification = (
        _ROOT
        / ".planning"
        / "phases"
        / "24-final-milestone-audit-archive-readiness-and-v1-3-handoff-prep"
        / "24-VERIFICATION.md"
    )

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert handoff.exists()
    assert phase_23_verification.exists()
    assert phase_24_verification.exists()

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
    )

    for path in archive_paths:
        assert path.exists()

    for needle in (
        "v1.1-ROADMAP.md",
        "v1.1-REQUIREMENTS.md",
        "v1.2-ROADMAP.md",
        "v1.2-REQUIREMENTS.md",
    ):
        assert needle in roadmap_text
        assert needle in requirements_text or needle in project_text or needle in milestones_text

    assert "archive snapshots 已落入 `.planning/milestones/`" in state_text
    assert "archived / evidence-ready" in milestones_text
    assert "archived snapshots created / handoff-ready" in milestones_text
    assert "revalidated 2026-03-17" in milestones_text

    v1_1_archive_text = (
        _ROOT / ".planning" / "milestones" / "v1.1-ROADMAP.md"
    ).read_text(encoding="utf-8")

    assert "待执行 milestone archival" not in v1_1_archive_text
    assert "当当前里程碑完成时，应能同时回答以下问题：" in project_text


def test_phase_28_to_31_continuation_assets_and_tracking_truth_are_synced() -> None:
    phase_assets = {
        "28-release-trust-gate-completion-and-maintainer-resilience": (
            "28-01-SUMMARY.md",
            "28-02-SUMMARY.md",
            "28-03-SUMMARY.md",
            "28-VERIFICATION.md",
            "28-VALIDATION.md",
        ),
        "29-rest-child-facade-slimming-and-test-topicization": (
            "29-01-SUMMARY.md",
            "29-02-SUMMARY.md",
            "29-03-SUMMARY.md",
            "29-VERIFICATION.md",
            "29-VALIDATION.md",
        ),
        "30-protocol-control-typed-contract-tightening": (
            "30-01-SUMMARY.md",
            "30-02-SUMMARY.md",
            "30-03-SUMMARY.md",
            "30-VERIFICATION.md",
            "30-VALIDATION.md",
        ),
        "31-runtime-service-typed-budget-and-exception-closure": (
            "31-01-SUMMARY.md",
            "31-02-SUMMARY.md",
            "31-03-SUMMARY.md",
            "31-04-SUMMARY.md",
            "31-VERIFICATION.md",
            "31-VALIDATION.md",
        ),
    }

    for phase_dir_name, filenames in phase_assets.items():
        phase_dir = _ROOT / ".planning" / "phases" / phase_dir_name
        for filename in filenames:
            assert (phase_dir / filename).exists()

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
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "32-truth-convergence-gate-honesty-and-quality-10-closeout"
    )
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    for artifact_name in (
        "32-CONTEXT.md",
        "32-RESEARCH.md",
        "32-01-PLAN.md",
        "32-02-PLAN.md",
        "32-03-PLAN.md",
        "32-04-PLAN.md",
        "32-05-PLAN.md",
        "32-VALIDATION.md",
        "32-01-SUMMARY.md",
        "32-02-SUMMARY.md",
        "32-03-SUMMARY.md",
        "32-04-SUMMARY.md",
        "32-05-SUMMARY.md",
        "32-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()

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
    assert "## Recommended Next Command" in state_text
    assert "$gsd-plan-milestone-gaps" in state_text
    assert "$gsd-complete-milestone v1.3" in state_text
    assert "$gsd-progress" in state_text


def test_phase_33_planning_truth_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "33-contract-truth-unification-hotspot-slimming-and-productization-hardening"
    )
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    for artifact_name in (
        "33-CONTEXT.md",
        "33-RESEARCH.md",
        "33-01-PLAN.md",
        "33-02-PLAN.md",
        "33-03-PLAN.md",
        "33-04-PLAN.md",
        "33-05-PLAN.md",
        "33-06-PLAN.md",
        "33-VALIDATION.md",
        "33-01-SUMMARY.md",
        "33-02-SUMMARY.md",
        "33-03-SUMMARY.md",
        "33-04-SUMMARY.md",
        "33-05-SUMMARY.md",
        "33-06-SUMMARY.md",
        "33-SUMMARY.md",
        "33-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()

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
    assert "## Recommended Next Command" in state_text
    assert "$gsd-plan-milestone-gaps" in state_text
    assert "$gsd-complete-milestone v1.3" in state_text
    assert "$gsd-progress" in state_text


def test_phase_34_planning_truth_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "34-continuity-and-hard-release-gates"
    )
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    for artifact_name in (
        "34-CONTEXT.md",
        "34-01-PLAN.md",
        "34-02-PLAN.md",
        "34-03-PLAN.md",
        "34-VALIDATION.md",
        "34-01-SUMMARY.md",
        "34-02-SUMMARY.md",
        "34-03-SUMMARY.md",
        "34-SUMMARY.md",
        "34-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()

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

    assert "## Recommended Next Command" in state_text
    assert "$gsd-progress" in state_text
    assert "$gsd-plan-milestone-gaps" in state_text
    assert "$gsd-complete-milestone v1.3" in state_text


def test_phase_35_planning_truth_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "35-protocol-hotspot-final-slimming"
    )
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    for artifact_name in (
        "35-CONTEXT.md",
        "35-01-PLAN.md",
        "35-02-PLAN.md",
        "35-03-PLAN.md",
        "35-VALIDATION.md",
        "35-01-SUMMARY.md",
        "35-02-SUMMARY.md",
        "35-03-SUMMARY.md",
        "35-SUMMARY.md",
        "35-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()

    assert "### Phase 35: Protocol hotspot final slimming" in roadmap_text
    assert "**Requirements**: [HOT-09, RES-07]" in roadmap_text
    assert "**Status**: Complete (`2026-03-18`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "| HOT-09 | Phase 35 | Complete |" in requirements_text
    assert "| RES-07 | Phase 35 | Complete |" in requirements_text
    assert "## Phase 35 Protocol Hotspot Slimming Update" in project_text
    assert "## Recommended Next Command" in state_text


def test_phase_36_planning_truth_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "36-runtime-root-and-exception-burn-down"
    )
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    for artifact_name in (
        "36-CONTEXT.md",
        "36-01-PLAN.md",
        "36-02-PLAN.md",
        "36-03-PLAN.md",
        "36-VALIDATION.md",
        "36-01-SUMMARY.md",
        "36-02-SUMMARY.md",
        "36-03-SUMMARY.md",
        "36-SUMMARY.md",
        "36-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()

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
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "37-test-topology-and-derived-truth-convergence"
    )
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    for artifact_name in (
        "37-CONTEXT.md",
        "37-01-PLAN.md",
        "37-02-PLAN.md",
        "37-03-PLAN.md",
        "37-VALIDATION.md",
        "37-01-SUMMARY.md",
        "37-02-SUMMARY.md",
        "37-03-SUMMARY.md",
        "37-SUMMARY.md",
        "37-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()

    assert "### Phase 37: Test topology and derived-truth convergence" in roadmap_text
    assert "**Requirements**: [TST-06, GOV-30, QLT-09]" in roadmap_text
    assert "**Status**: Complete (`2026-03-18`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "| TST-06 | Phase 37 | Complete |" in requirements_text
    assert "| GOV-30 | Phase 37 | Complete |" in requirements_text
    assert "| QLT-09 | Phase 37 | Complete |" in requirements_text
    assert "## Phase 37 Test Topology & Derived-Truth Update" in project_text
    assert "**Default next step:** `$gsd-progress`" in project_text
    assert "## Recommended Next Command" in state_text
    assert "$gsd-plan-phase 39" in state_text


def test_phase_38_planning_truth_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "38-external-boundary-residual-retirement-and-quality-signal-hardening"
    )
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )

    for artifact_name in (
        "38-CONTEXT.md",
        "38-01-PLAN.md",
        "38-02-PLAN.md",
        "38-03-PLAN.md",
        "38-VALIDATION.md",
        "38-01-SUMMARY.md",
        "38-02-SUMMARY.md",
        "38-03-SUMMARY.md",
        "38-SUMMARY.md",
        "38-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()

    assert "### Phase 38: External-boundary residual retirement and quality-signal hardening" in roadmap_text
    assert "**Requirements**: [RES-08, QLT-10, GOV-31]" in roadmap_text
    assert "**Status**: Complete (`2026-03-18`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "| RES-08 | Phase 38 | Complete |" in requirements_text
    assert "| QLT-10 | Phase 38 | Complete |" in requirements_text
    assert "| GOV-31 | Phase 38 | Complete |" in requirements_text
    assert "## Phase 38 External-Boundary Residual & Quality-Signal Hardening Update" in project_text
    assert "**Default next step:** `$gsd-progress`" in project_text
    assert "`Phase 38 complete`" in state_text
    assert "$gsd-plan-phase 39" in state_text
    assert "| _None_ | — | — | — | Phase 38 已关闭最后一条已登记 residual family。 |" in residual_text
    assert "## Phase 38 Residual Delta" in residual_text
