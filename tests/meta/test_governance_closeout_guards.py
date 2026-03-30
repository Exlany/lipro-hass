"""Governance closeout smoke and promoted-asset manifest guards."""

from __future__ import annotations

from .conftest import _load_frontmatter
from .governance_contract_helpers import _ROOT
from .governance_current_truth import LATEST_ARCHIVED_EVIDENCE_PATH
from .governance_promoted_assets import (
    _PROMOTED_PHASE_ASSETS,
    _assert_exact_promoted_phase_assets,
    _assert_phase_assets_not_promoted,
    _load_promoted_phase_assets,
)


def test_promoted_phase_assets_manifest_enforces_explicit_ci_evidence() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    manifest_text = _PROMOTED_PHASE_ASSETS.read_text(encoding="utf-8")
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
    assert "promoted phase evidence allowlist" in authority_text
    assert ".planning/reviews/PROMOTED_PHASE_ASSETS.md" in verification_text
    assert "未被 allowlist 显式列出的 `*-SUMMARY.md`、`*-VERIFICATION.md`、`*-VALIDATION.md`" in manifest_text

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


def test_phase_88_closeout_contract_aligns_verification_and_file_matrix() -> None:
    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    file_matrix_text = (
        _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
    ).read_text(encoding="utf-8")

    assert "## Phase 88 Governance Sync / Quality Proof / Milestone Freeze" in verification_text
    assert "historical phase-completion next-step = `$gsd-complete-milestone v1.23`" in verification_text
    assert "default next command = `$gsd-new-milestone`" in verification_text
    assert f"**Latest archived pointer:** `{LATEST_ARCHIVED_EVIDENCE_PATH}`" in verification_text
    for token in (
        "tests/meta/test_governance_bootstrap_smoke.py",
        "tests/meta/test_governance_closeout_guards.py",
        "tests/meta/test_governance_promoted_phase_assets.py",
        "tests/meta/test_governance_route_handoff_smoke.py",
        "tests/meta/governance_followup_route_current_milestones.py",
        "tests/meta/test_governance_release_contract.py",
        "tests/meta/test_governance_release_docs.py",
        "tests/meta/test_governance_release_continuity.py",
        "tests/meta/test_governance_milestone_archives.py",
        "tests/meta/test_phase88_governance_quality_freeze_guards.py",
    ):
        assert token in verification_text
    assert "node \"$HOME/.codex/get-shit-done/bin/gsd-tools.cjs\" init progress" in verification_text
    assert "uv run python scripts/check_file_matrix.py --check" in verification_text

    row_expectations = {
        "tests/meta/governance_contract_helpers.py": "shared governance route/doc helper home",
        "tests/meta/governance_current_truth.py": "governance-route contract + shared current/latest archive truth helper",
        "tests/meta/governance_promoted_assets.py": "shared promoted-phase-asset helper home",
        "tests/meta/test_governance_bootstrap_smoke.py": "focused bootstrap smoke guard home",
        "tests/meta/test_governance_route_handoff_smoke.py": "route-handoff gsd fast-path smoke guard home",
        "tests/meta/test_governance_closeout_guards.py": "closeout + promoted-asset manifest smoke anchor + milestone-freeze exit-contract bridge",
        "tests/meta/test_phase88_governance_quality_freeze_guards.py": "focused guard home for phase-88 governance/evidence freeze",
        "tests/meta/governance_followup_route_current_milestones.py": "governance-route contract + current/latest archive pointer-drift guard",
        "tests/meta/test_governance_release_contract.py": "release/governance workflow anchor suite",
        "tests/meta/test_governance_release_docs.py": "release/docs topic suite home",
        "tests/meta/test_governance_release_continuity.py": "release continuity/custody topic suite home",
    }
    for relative_path, residual_story in row_expectations.items():
        assert relative_path in file_matrix_text
        assert residual_story in file_matrix_text
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
    _assert_phase_assets_not_promoted(
        "43-control-services-boundary-decoupling-and-typed-runtime-access",
        "43-CONTEXT.md",
        "43-RESEARCH.md",
        "43-01-PLAN.md",
        "43-02-PLAN.md",
        "43-03-PLAN.md",
        "43-04-PLAN.md",
        "43-01-SUMMARY.md",
        "43-02-SUMMARY.md",
        "43-03-SUMMARY.md",
        "43-04-SUMMARY.md",
    )


def test_v1_20_promoted_allowlist_exactly_matches_audited_closeout_bundles() -> None:
    _assert_exact_promoted_phase_assets(
        "72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement",
        "72-01-SUMMARY.md",
        "72-02-SUMMARY.md",
        "72-03-SUMMARY.md",
        "72-04-SUMMARY.md",
        "72-VERIFICATION.md",
        "72-VALIDATION.md",
    )
    _assert_exact_promoted_phase_assets(
        "73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization",
        "73-01-SUMMARY.md",
        "73-02-SUMMARY.md",
        "73-03-SUMMARY.md",
        "73-04-SUMMARY.md",
        "73-VERIFICATION.md",
        "73-VALIDATION.md",
    )
    _assert_exact_promoted_phase_assets(
        "74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout",
        "74-01-SUMMARY.md",
        "74-02-SUMMARY.md",
        "74-03-SUMMARY.md",
        "74-04-SUMMARY.md",
        "74-VERIFICATION.md",
        "74-VALIDATION.md",
    )


def test_v1_20_promoted_allowlist_does_not_widen_into_execution_traces() -> None:
    for phase_dir_name, prefix in (
        ("72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement", "72"),
        ("73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization", "73"),
        ("74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout", "74"),
    ):
        _assert_phase_assets_not_promoted(phase_dir_name, f"{prefix}-CONTEXT.md", f"{prefix}-RESEARCH.md", f"{prefix}-01-PLAN.md")

    _assert_phase_assets_not_promoted(
        "75-access-mode-truth-closure-evidence-promotion-formalization-and-thin-adapter-typing-hardening",
        "75-CONTEXT.md",
        "75-RESEARCH.md",
        "75-01-PLAN.md",
        "75-01-SUMMARY.md",
        "75-VERIFICATION.md",
        "75-VALIDATION.md",
    )


def test_v1_23_promoted_allowlist_exactly_matches_closeout_bundles() -> None:
    _assert_exact_promoted_phase_assets(
        "85-terminal-audit-refresh-and-residual-routing",
        "85-01-SUMMARY.md",
        "85-02-SUMMARY.md",
        "85-03-SUMMARY.md",
    )
    _assert_exact_promoted_phase_assets(
        "86-production-residual-eradication-and-boundary-re-tightening",
        "86-01-SUMMARY.md",
        "86-02-SUMMARY.md",
        "86-03-SUMMARY.md",
        "86-04-SUMMARY.md",
        "86-VALIDATION.md",
    )
    _assert_exact_promoted_phase_assets(
        "87-assurance-hotspot-decomposition-and-no-regrowth-guards",
        "87-01-SUMMARY.md",
        "87-02-SUMMARY.md",
        "87-03-SUMMARY.md",
        "87-04-SUMMARY.md",
    )
    _assert_exact_promoted_phase_assets(
        "88-governance-sync-quality-proof-and-milestone-freeze",
        "88-01-SUMMARY.md",
        "88-02-SUMMARY.md",
        "88-03-SUMMARY.md",
        "88-SUMMARY.md",
        "88-VERIFICATION.md",
        "88-VALIDATION.md",
    )



def test_v1_29_phase105_promoted_allowlist_matches_closeout_bundle() -> None:
    _assert_exact_promoted_phase_assets(
        "105-governance-rule-datafication-and-milestone-freeze",
        "105-01-SUMMARY.md",
        "105-02-SUMMARY.md",
        "105-03-SUMMARY.md",
        "105-SUMMARY.md",
        "105-VERIFICATION.md",
        "105-VALIDATION.md",
    )

