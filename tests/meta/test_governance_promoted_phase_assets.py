"""Governance guards for promoted phase-asset families."""

from __future__ import annotations

from .test_governance_closeout_guards import _ROOT, _assert_promoted_phase_assets


def test_phase_43_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "43-control-services-boundary-decoupling-and-typed-runtime-access",
        "43-SUMMARY.md",
        "43-VERIFICATION.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (
        _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
    ).read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 43 Control / Runtime / Service Boundary Contract" in verification_text
    assert "## Phase 43 Residual Delta" in residual_text
    assert "## Phase 43 Status Update" in kill_text


def test_phase_44_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "44-governance-asset-pruning-and-terminology-convergence",
        "44-SUMMARY.md",
        "44-VERIFICATION.md",
    )

    docs_text = (_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    file_matrix_text = (
        _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (
        _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
    ).read_text(encoding="utf-8")
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
    file_matrix_text = (
        _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (
        _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
    ).read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 45 Hotspot / Typed Failure / Benchmark Contract" in verification_text
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
    residual_text = (
        _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
    ).read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 52 Protocol-Root Second-Round Slimming and Request-Policy Isolation Contract" in verification_text
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
    file_matrix_text = (
        _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
    ).read_text(encoding="utf-8")

    assert "## Phase 53 Runtime and Entry-Root Second-Round Throttling Contract" in verification_text
    assert "custom_components/lipro/control/entry_root_wiring.py" in file_matrix_text
    assert "custom_components/lipro/core/coordinator/runtime_wiring.py" in file_matrix_text


def test_phase_54_closeout_assets_exist_and_are_promoted() -> None:
    _assert_promoted_phase_assets(
        "54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families",
        "54-SUMMARY.md",
        "54-VERIFICATION.md",
    )

    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (
        _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
    ).read_text(encoding="utf-8")
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
    file_matrix_text = (
        _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
    ).read_text(encoding="utf-8")

    assert "## Phase 55 Mega-Test Topicization and Typing Stratification Contract" in verification_text
    assert "production_any" in testing_text
    assert "test_switch_behavior.py" in file_matrix_text
    assert "test_transport_runtime_lifecycle.py" in file_matrix_text

