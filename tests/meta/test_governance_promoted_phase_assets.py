"""Governance guards for promoted phase-asset families."""

from __future__ import annotations

from .governance_promoted_assets import (
    _ROOT,
    _assert_phase_assets_not_promoted,
    _assert_promoted_phase_assets,
)


def test_phase_43_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "43-control-services-boundary-decoupling-and-typed-runtime-access",
        "43-SUMMARY.md",
        "43-VERIFICATION.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert (
        "## Phase 43 Control / Runtime / Service Boundary Contract" in verification_text
    )
    assert "## Phase 43 Residual Delta" in residual_text
    assert "## Phase 43 Status Update" in kill_text


def test_phase_44_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "44-governance-asset-pruning-and-terminology-convergence",
        "44-SUMMARY.md",
        "44-VERIFICATION.md",
    )

    docs_text = (_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "Public Fast Path" in docs_text
    assert "Bilingual Boundary" in docs_text
    assert "tests/meta/test_governance_closeout_guards.py" in file_matrix_text
    assert "tests/meta/test_toolchain_truth.py" in file_matrix_text
    assert "## Phase 44 Residual Delta" in residual_text
    assert "## Phase 44 Status Update" in kill_text


def test_phase_45_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "45-hotspot-decomposition-and-typed-failure-semantics",
        "45-SUMMARY.md",
        "45-VERIFICATION.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert (
        "## Phase 45 Hotspot / Typed Failure / Benchmark Contract" in verification_text
    )
    assert "scripts/check_benchmark_baseline.py" in file_matrix_text
    assert "tests/meta/test_phase45_hotspot_budget_guards.py" in file_matrix_text
    assert "## Phase 45 Residual Delta" in residual_text
    assert "## Phase 45 Status Update" in kill_text


def test_phase_46_audit_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "46-exhaustive-repository-audit-standards-conformance-and-remediation-routing",
        "46-AUDIT.md",
        "46-SCORE-MATRIX.md",
        "46-REMEDIATION-ROADMAP.md",
        "46-SUMMARY.md",
        "46-VERIFICATION.md",
    )

    reviews_text = (_ROOT / ".planning" / "reviews" / "README.md").read_text(
        encoding="utf-8"
    )
    verification_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "46-exhaustive-repository-audit-standards-conformance-and-remediation-routing"
        / "46-VERIFICATION.md"
    ).read_text(encoding="utf-8")

    assert "promoted audit package" in reviews_text
    assert "46-AUDIT.md" in reviews_text
    assert "46-REMEDIATION-ROADMAP.md" in reviews_text
    assert "status:" in verification_text


def test_phase_52_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "52-protocol-root-second-round-slimming-and-request-policy-isolation",
        "52-SUMMARY.md",
        "52-VERIFICATION.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert (
        "## Phase 52 Protocol-Root Second-Round Slimming and Request-Policy Isolation Contract"
        in verification_text
    )
    assert "## Phase 52 Residual Delta" in residual_text
    assert "## Phase 52 Status Update" in kill_text


def test_phase_53_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "53-runtime-and-entry-root-second-round-throttling",
        "53-SUMMARY.md",
        "53-VERIFICATION.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )

    assert (
        "## Phase 53 Runtime and Entry-Root Second-Round Throttling Contract"
        in verification_text
    )
    assert "custom_components/lipro/control/entry_root_wiring.py" in file_matrix_text
    assert (
        "custom_components/lipro/core/coordinator/runtime_wiring.py" in file_matrix_text
    )


def test_phase_54_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families",
        "54-SUMMARY.md",
        "54-VERIFICATION.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 54 Helper-Hotspot Formalization Contract" in verification_text
    assert "Phase 56+" in residual_text
    assert "## Phase 54 Status Update" in kill_text


def test_phase_55_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification",
        "55-SUMMARY.md",
        "55-VERIFICATION.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    testing_text = (_ROOT / ".planning" / "codebase" / "TESTING.md").read_text(
        encoding="utf-8"
    )
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )

    assert (
        "## Phase 55 Mega-Test Topicization and Typing Stratification Contract"
        in verification_text
    )
    assert "production_any" in testing_text
    assert "test_switch_behavior.py" in file_matrix_text
    assert "test_transport_runtime_lifecycle.py" in file_matrix_text


def test_phase_66_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening",
        "66-01-SUMMARY.md",
        "66-02-SUMMARY.md",
        "66-03-SUMMARY.md",
        "66-04-SUMMARY.md",
        "66-SUMMARY.md",
        "66-VERIFICATION.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 66 Exit Contract" in verification_text
    assert "## Phase 66 Residual Delta" in residual_text
    assert "## Phase 66 Status Update" in kill_text


def test_phase_72_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement",
        "72-01-SUMMARY.md",
        "72-02-SUMMARY.md",
        "72-03-SUMMARY.md",
        "72-04-SUMMARY.md",
        "72-VERIFICATION.md",
        "72-VALIDATION.md",
    )

    audit_text = (_ROOT / ".planning" / "v1.20-MILESTONE-AUDIT.md").read_text(
        encoding="utf-8"
    )

    assert "72-04-SUMMARY.md" in audit_text
    assert "72-VERIFICATION.md" in audit_text
    assert "72-VALIDATION.md" in audit_text


def test_phase_73_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization",
        "73-01-SUMMARY.md",
        "73-02-SUMMARY.md",
        "73-03-SUMMARY.md",
        "73-04-SUMMARY.md",
        "73-VERIFICATION.md",
        "73-VALIDATION.md",
    )

    audit_text = (_ROOT / ".planning" / "v1.20-MILESTONE-AUDIT.md").read_text(
        encoding="utf-8"
    )

    assert "73-04-SUMMARY.md" in audit_text
    assert "73-VERIFICATION.md" in audit_text
    assert "73-VALIDATION.md" in audit_text


def test_phase_74_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout",
        "74-01-SUMMARY.md",
        "74-02-SUMMARY.md",
        "74-03-SUMMARY.md",
        "74-04-SUMMARY.md",
        "74-VERIFICATION.md",
        "74-VALIDATION.md",
    )

    audit_text = (_ROOT / ".planning" / "v1.20-MILESTONE-AUDIT.md").read_text(
        encoding="utf-8"
    )

    assert "74-04-SUMMARY.md" in audit_text
    assert "74-VERIFICATION.md" in audit_text
    assert "74-VALIDATION.md" in audit_text


def test_phase_76_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation",
        "76-01-SUMMARY.md",
        "76-02-SUMMARY.md",
        "76-03-SUMMARY.md",
        "76-VERIFICATION.md",
        "76-VALIDATION.md",
    )


def test_phase_77_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction",
        "77-01-SUMMARY.md",
        "77-02-SUMMARY.md",
        "77-03-SUMMARY.md",
        "77-VERIFICATION.md",
        "77-VALIDATION.md",
    )


def test_phase_78_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "78-quality-gate-formalization-route-handoff-ergonomics-and-milestone-closeout-readiness",
        "78-01-SUMMARY.md",
        "78-02-SUMMARY.md",
        "78-03-SUMMARY.md",
        "78-SUMMARY.md",
        "78-VERIFICATION.md",
        "78-VALIDATION.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 78 Exit Contract" in verification_text
    assert "## Phase 78 Residual Delta" in residual_text
    assert "## Phase 78 Status Update" in kill_text


def test_phase_79_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "79-governance-tooling-hotspot-decomposition-and-release-contract-topicization",
        "79-01-SUMMARY.md",
        "79-02-SUMMARY.md",
        "79-03-SUMMARY.md",
        "79-SUMMARY.md",
        "79-VERIFICATION.md",
        "79-VALIDATION.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 79 Exit Contract" in verification_text
    assert "## Phase 79 Residual Delta" in residual_text
    assert "## Phase 79 Status Update" in kill_text


def test_phase_80_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "80-governance-typing-closure-and-final-meta-suite-hotspot-topicization",
        "80-01-SUMMARY.md",
        "80-02-SUMMARY.md",
        "80-03-SUMMARY.md",
        "80-SUMMARY.md",
        "80-VERIFICATION.md",
        "80-VALIDATION.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 80 Exit Contract" in verification_text
    assert "## Phase 80 Residual Delta" in residual_text
    assert "## Phase 80 Status Update" in kill_text


def test_phase_81_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "81-contributor-onramp-route-convergence-and-public-entry-contract",
        "81-01-SUMMARY.md",
        "81-02-SUMMARY.md",
        "81-03-SUMMARY.md",
        "81-SUMMARY.md",
        "81-VERIFICATION.md",
        "81-VALIDATION.md",
    )


def test_phase_82_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "82-release-operations-closure-and-evidence-chain-formalization",
        "82-01-SUMMARY.md",
        "82-02-SUMMARY.md",
        "82-03-SUMMARY.md",
        "82-SUMMARY.md",
        "82-VERIFICATION.md",
        "82-VALIDATION.md",
    )


def test_phase_83_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "83-intake-templates-and-maintainer-stewardship-contract",
        "83-01-SUMMARY.md",
        "83-02-SUMMARY.md",
        "83-03-SUMMARY.md",
        "83-SUMMARY.md",
        "83-VERIFICATION.md",
        "83-VALIDATION.md",
    )
    _assert_phase_assets_not_promoted(
        "83-intake-templates-and-maintainer-stewardship-contract",
        "83-CONTEXT.md",
        "83-RESEARCH.md",
        "83-01-PLAN.md",
        "83-02-PLAN.md",
        "83-03-PLAN.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 83 Intake / Stewardship Contract" in verification_text
    assert "## Phase 83 Residual Delta" in residual_text
    assert "## Phase 83 Status Update" in kill_text


def test_phase_84_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "84-governance-open-source-guard-coverage-and-milestone-truth-freeze",
        "84-01-SUMMARY.md",
        "84-02-SUMMARY.md",
        "84-03-SUMMARY.md",
        "84-SUMMARY.md",
        "84-VERIFICATION.md",
        "84-VALIDATION.md",
    )
    _assert_phase_assets_not_promoted(
        "84-governance-open-source-guard-coverage-and-milestone-truth-freeze",
        "84-CONTEXT.md",
        "84-DISCUSSION-LOG.md",
        "84-RESEARCH.md",
        "84-01-PLAN.md",
        "84-02-PLAN.md",
        "84-03-PLAN.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 84 Governance / Open-Source Guard Freeze" in verification_text
    assert "## Phase 84 Residual Delta" in residual_text
    assert "## Phase 84 Status Update" in kill_text


def test_phase_88_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "88-governance-sync-quality-proof-and-milestone-freeze",
        "88-01-SUMMARY.md",
        "88-02-SUMMARY.md",
        "88-03-SUMMARY.md",
        "88-SUMMARY.md",
        "88-VERIFICATION.md",
        "88-VALIDATION.md",
    )
    _assert_phase_assets_not_promoted(
        "88-governance-sync-quality-proof-and-milestone-freeze",
        "88-CONTEXT.md",
        "88-DISCUSSION-LOG.md",
        "88-RESEARCH.md",
        "88-01-PLAN.md",
        "88-02-PLAN.md",
        "88-03-PLAN.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )
    audit_text = (
        _ROOT / ".planning" / "reviews" / "V1_23_TERMINAL_AUDIT.md"
    ).read_text(encoding="utf-8")

    assert (
        "## Phase 88 Governance Sync / Quality Proof / Milestone Freeze"
        in verification_text
    )
    assert "Phase 88 freeze note" in residual_text
    assert "## Phase 85 Routed Delete Gates" in kill_text
    assert "Historical review artifact" in audit_text


def test_phase_89_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence",
        "89-01-SUMMARY.md",
        "89-02-SUMMARY.md",
        "89-03-SUMMARY.md",
        "89-04-SUMMARY.md",
        "89-VERIFICATION.md",
        "89-VALIDATION.md",
    )
    _assert_phase_assets_not_promoted(
        "89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence",
        "89-CONTEXT.md",
        "89-PRD.md",
        "89-RESEARCH.md",
        "89-01-PLAN.md",
        "89-02-PLAN.md",
        "89-03-PLAN.md",
        "89-04-PLAN.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")

    assert (
        "## Phase 89 Runtime Boundary Tightening / Tooling Kernel Decoupling / Open-Source Entry Convergence"
        in verification_text
    )


def test_phase_102_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "102-governance-portability-verification-stratification-and-open-source-continuity-hardening",
        "102-01-SUMMARY.md",
        "102-02-SUMMARY.md",
        "102-03-SUMMARY.md",
        "102-VERIFICATION.md",
        "102-VALIDATION.md",
    )


def test_phase_105_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "105-governance-rule-datafication-and-milestone-freeze",
        "105-01-SUMMARY.md",
        "105-02-SUMMARY.md",
        "105-03-SUMMARY.md",
        "105-SUMMARY.md",
        "105-VERIFICATION.md",
        "105-VALIDATION.md",
    )


def test_phase_129_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "129-rest-fallback-explicit-surface-convergence-and-api-hotspot-slimming",
        "129-01-SUMMARY.md",
        "129-02-SUMMARY.md",
        "129-SUMMARY.md",
        "129-VERIFICATION.md",
        "129-VALIDATION.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")

    assert "## Phase 129 Exit Contract" in verification_text


def test_phase_130_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "130-runtime-command-and-firmware-update-hotspot-decomposition",
        "130-01-SUMMARY.md",
        "130-02-SUMMARY.md",
        "130-SUMMARY.md",
        "130-VERIFICATION.md",
        "130-VALIDATION.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 130 Exit Contract" in verification_text
    assert "## Phase 130 Residual Delta" in residual_text
    assert "## Phase 130 Status Update" in kill_text


def test_phase_131_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "131-repo-wide-terminal-audit-closeout-and-governance-continuity-decisions",
        "131-01-SUMMARY.md",
        "131-02-SUMMARY.md",
        "131-03-SUMMARY.md",
        "131-SUMMARY.md",
        "131-VERIFICATION.md",
        "131-VALIDATION.md",
        "131-TERMINAL-AUDIT.md",
    )
    _assert_phase_assets_not_promoted(
        "131-repo-wide-terminal-audit-closeout-and-governance-continuity-decisions",
        "131-CONTEXT.md",
        "131-RESEARCH.md",
        "131-01-PLAN.md",
        "131-02-PLAN.md",
        "131-03-PLAN.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 131 Exit Contract" in verification_text
    assert "## Phase 131 Residual Delta" in residual_text
    assert "## Phase 131 Status Update" in kill_text
