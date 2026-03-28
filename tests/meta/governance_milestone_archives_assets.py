"""Milestone-archive asset existence guards."""
from __future__ import annotations

from .governance_contract_helpers import _ROOT, assert_pull_only_evidence_index
from .governance_promoted_assets import _assert_promoted_phase_assets


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

def test_v1_5_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_5_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.5-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.5-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.5-REQUIREMENTS.md").exists()
    assert (
        _ROOT
        / ".planning"
        / "phases"
        / "40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification"
        / "40-VALIDATION.md"
    ).exists()
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

def test_v1_6_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_6_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.6-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.6-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.6-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "42-delivery-trust-gates-and-validation-hardening",
        "42-SUMMARY.md",
        "42-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "43-control-services-boundary-decoupling-and-typed-runtime-access",
        "43-SUMMARY.md",
        "43-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "44-governance-asset-pruning-and-terminology-convergence",
        "44-SUMMARY.md",
        "44-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "45-hotspot-decomposition-and-typed-failure-semantics",
        "45-SUMMARY.md",
        "45-VERIFICATION.md",
    )

    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    assert "42-VERIFICATION.md" in evidence_text
    assert "43-VERIFICATION.md" in evidence_text
    assert "44-VERIFICATION.md" in evidence_text
    assert "45-VERIFICATION.md" in evidence_text
    assert "archive-ready / shipped" in evidence_text
    assert "V1_6_EVIDENCE_INDEX.md" in evidence_text

def test_v1_14_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_14_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.14-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.14-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.14-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "63-governance-truth-realignment-typed-runtime-access-and-hidden-root-closure",
        "63-SUMMARY.md",
        "63-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "64-telemetry-typing-schedule-contracts-and-diagnostics-hotspot-slimming",
        "64-SUMMARY.md",
        "64-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure",
        "65-SUMMARY.md",
        "65-VERIFICATION.md",
    )
    _assert_promoted_phase_assets(
        "66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening",
        "66-SUMMARY.md",
        "66-VERIFICATION.md",
    )

    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    assert "63-VERIFICATION.md" in evidence_text
    assert "64-VERIFICATION.md" in evidence_text
    assert "65-VERIFICATION.md" in evidence_text
    assert "66-VERIFICATION.md" in evidence_text
    assert "archived / evidence-ready" in evidence_text
    assert "V1_14_EVIDENCE_INDEX.md" in evidence_text

def test_v1_15_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_15_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.15-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.15-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.15-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "67-typed-contract-convergence-toolchain-hardening-and-mypy-closure",
        "67-SUMMARY.md",
        "67-VERIFICATION.md",
    )

    assert_pull_only_evidence_index(
        evidence_index,
        "67-SUMMARY.md",
        "67-VERIFICATION.md",
        "67-VALIDATION.md",
        "archived / evidence-ready",
        "V1_15_EVIDENCE_INDEX.md",
    )

def test_v1_16_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_16_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.16-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.16-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.16-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening",
        "68-SUMMARY.md",
        "68-VERIFICATION.md",
    )

    assert_pull_only_evidence_index(
        evidence_index,
        "68-SUMMARY.md",
        "68-VERIFICATION.md",
        "68-VALIDATION.md",
        "carry-forward",
        "V1_16_EVIDENCE_INDEX.md",
    )

def test_v1_17_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_17_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.17-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.17-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.17-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "69-residual-read-model-quality-balance-and-open-source-contract-closure",
        "69-SUMMARY.md",
        "69-VERIFICATION.md",
    )

    assert_pull_only_evidence_index(
        evidence_index,
        "69-SUMMARY.md",
        "69-VERIFICATION.md",
        "69-VALIDATION.md",
        "archived / evidence-ready",
        "V1_17_EVIDENCE_INDEX.md",
    )

def test_v1_18_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_18_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.18-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.18-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.18-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization",
        "70-SUMMARY.md",
        "70-VERIFICATION.md",
    )

    assert_pull_only_evidence_index(
        evidence_index,
        "70-SUMMARY.md",
        "70-VERIFICATION.md",
        "70-VALIDATION.md",
        "archived / evidence-ready",
        "V1_18_EVIDENCE_INDEX.md",
    )

def test_v1_19_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_19_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.19-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.19-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.19-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection",
        "71-SUMMARY.md",
        "71-VERIFICATION.md",
    )

    assert_pull_only_evidence_index(
        evidence_index,
        "71-SUMMARY.md",
        "71-VERIFICATION.md",
        "71-VALIDATION.md",
        "archived / evidence-ready",
        "V1_19_EVIDENCE_INDEX.md",
    )

def test_v1_20_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_20_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.20-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.20-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.20-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement",
        "72-01-SUMMARY.md",
        "72-02-SUMMARY.md",
        "72-03-SUMMARY.md",
        "72-04-SUMMARY.md",
        "72-VERIFICATION.md",
        "72-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization",
        "73-01-SUMMARY.md",
        "73-02-SUMMARY.md",
        "73-03-SUMMARY.md",
        "73-04-SUMMARY.md",
        "73-VERIFICATION.md",
        "73-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout",
        "74-01-SUMMARY.md",
        "74-02-SUMMARY.md",
        "74-03-SUMMARY.md",
        "74-04-SUMMARY.md",
        "74-VERIFICATION.md",
        "74-VALIDATION.md",
    )

    assert_pull_only_evidence_index(
        evidence_index,
        "72-VERIFICATION.md",
        "73-VERIFICATION.md",
        "74-VERIFICATION.md",
        "archived / evidence-ready",
        "V1_20_EVIDENCE_INDEX.md",
    )

def test_v1_22_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_22_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.22-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.22-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.22-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "81-contributor-onramp-route-convergence-and-public-entry-contract",
        "81-01-SUMMARY.md",
        "81-02-SUMMARY.md",
        "81-03-SUMMARY.md",
        "81-SUMMARY.md",
        "81-VERIFICATION.md",
        "81-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "82-release-operations-closure-and-evidence-chain-formalization",
        "82-01-SUMMARY.md",
        "82-02-SUMMARY.md",
        "82-03-SUMMARY.md",
        "82-SUMMARY.md",
        "82-VERIFICATION.md",
        "82-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "83-intake-templates-and-maintainer-stewardship-contract",
        "83-01-SUMMARY.md",
        "83-02-SUMMARY.md",
        "83-03-SUMMARY.md",
        "83-SUMMARY.md",
        "83-VERIFICATION.md",
        "83-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "84-governance-open-source-guard-coverage-and-milestone-truth-freeze",
        "84-01-SUMMARY.md",
        "84-02-SUMMARY.md",
        "84-03-SUMMARY.md",
        "84-SUMMARY.md",
        "84-VERIFICATION.md",
        "84-VALIDATION.md",
    )

    assert_pull_only_evidence_index(
        evidence_index,
        "81-VERIFICATION.md",
        "82-VERIFICATION.md",
        "84-VALIDATION.md",
        "archived / evidence-ready",
        "V1_22_EVIDENCE_INDEX.md",
    )



def test_v1_24_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_24_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.24-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.24-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.24-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence",
        "89-01-SUMMARY.md",
        "89-02-SUMMARY.md",
        "89-03-SUMMARY.md",
        "89-04-SUMMARY.md",
        "89-VERIFICATION.md",
        "89-VALIDATION.md",
    )

    assert_pull_only_evidence_index(
        evidence_index,
        "89-04-SUMMARY.md",
        "89-VERIFICATION.md",
        "89-VALIDATION.md",
        "archived / evidence-ready",
        "V1_24_EVIDENCE_INDEX.md",
    )

def test_v1_26_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_26_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.26-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.26-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.26-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "94-typed-payload-contraction-and-domain-bag-narrowing",
        "94-01-SUMMARY.md",
        "94-02-SUMMARY.md",
        "94-03-SUMMARY.md",
        "94-VERIFICATION.md",
        "94-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "95-schedule-runtime-and-boundary-hotspot-inward-decomposition",
        "95-01-SUMMARY.md",
        "95-02-SUMMARY.md",
        "95-03-SUMMARY.md",
        "95-VERIFICATION.md",
        "95-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "96-redaction-telemetry-and-anonymous-share-sanitizer-burndown",
        "96-01-SUMMARY.md",
        "96-02-SUMMARY.md",
        "96-03-SUMMARY.md",
        "96-VERIFICATION.md",
        "96-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "97-governance-open-source-contract-sync-and-assurance-freeze",
        "97-01-SUMMARY.md",
        "97-02-SUMMARY.md",
        "97-03-SUMMARY.md",
        "97-VERIFICATION.md",
        "97-VALIDATION.md",
    )

    assert_pull_only_evidence_index(
        evidence_index,
        "94-VERIFICATION.md",
        "95-VERIFICATION.md",
        "96-VERIFICATION.md",
        "97-VERIFICATION.md",
        "97-VALIDATION.md",
        "archived / evidence-ready",
        "V1_26_EVIDENCE_INDEX.md",
    )

def test_v1_25_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_25_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.25-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.25-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.25-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "90-hotspot-routing-freeze-and-formal-home-decomposition-map",
        "90-01-SUMMARY.md",
        "90-02-SUMMARY.md",
        "90-03-SUMMARY.md",
        "90-VERIFICATION.md",
        "90-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "91-protocol-runtime-decomposition-and-typed-boundary-hardening",
        "91-01-SUMMARY.md",
        "91-02-SUMMARY.md",
        "91-03-SUMMARY.md",
        "91-VERIFICATION.md",
        "91-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "92-control-entity-thin-boundary-and-redaction-convergence",
        "92-01-SUMMARY.md",
        "92-02-SUMMARY.md",
        "92-03-SUMMARY.md",
        "92-VERIFICATION.md",
        "92-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "93-assurance-topicization-and-quality-freeze",
        "93-01-SUMMARY.md",
        "93-02-SUMMARY.md",
        "93-03-SUMMARY.md",
        "93-VERIFICATION.md",
        "93-VALIDATION.md",
    )

    assert_pull_only_evidence_index(
        evidence_index,
        "90-VERIFICATION.md",
        "91-VERIFICATION.md",
        "92-VERIFICATION.md",
        "93-VERIFICATION.md",
        "93-VALIDATION.md",
        "archived / evidence-ready",
        "V1_25_EVIDENCE_INDEX.md",
    )

def test_v1_23_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_23_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.23-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.23-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.23-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "85-terminal-audit-refresh-and-residual-routing",
        "85-01-SUMMARY.md",
        "85-02-SUMMARY.md",
        "85-03-SUMMARY.md",
    )
    _assert_promoted_phase_assets(
        "86-production-residual-eradication-and-boundary-re-tightening",
        "86-01-SUMMARY.md",
        "86-02-SUMMARY.md",
        "86-03-SUMMARY.md",
        "86-04-SUMMARY.md",
        "86-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "87-assurance-hotspot-decomposition-and-no-regrowth-guards",
        "87-01-SUMMARY.md",
        "87-02-SUMMARY.md",
        "87-03-SUMMARY.md",
        "87-04-SUMMARY.md",
    )
    _assert_promoted_phase_assets(
        "88-governance-sync-quality-proof-and-milestone-freeze",
        "88-01-SUMMARY.md",
        "88-02-SUMMARY.md",
        "88-03-SUMMARY.md",
        "88-SUMMARY.md",
        "88-VERIFICATION.md",
        "88-VALIDATION.md",
    )

    assert_pull_only_evidence_index(
        evidence_index,
        "85-03-SUMMARY.md",
        "86-VALIDATION.md",
        "88-VERIFICATION.md",
        "archived / evidence-ready",
        "V1_23_EVIDENCE_INDEX.md",
    )

def test_v1_21_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_21_EVIDENCE_INDEX.md"
    milestone_audit = _ROOT / ".planning" / "v1.21-MILESTONE-AUDIT.md"

    assert evidence_index.exists()
    assert milestone_audit.exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.21-ROADMAP.md").exists()
    assert (_ROOT / ".planning" / "milestones" / "v1.21-REQUIREMENTS.md").exists()
    _assert_promoted_phase_assets(
        "76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation",
        "76-01-SUMMARY.md",
        "76-02-SUMMARY.md",
        "76-03-SUMMARY.md",
        "76-VERIFICATION.md",
        "76-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction",
        "77-01-SUMMARY.md",
        "77-02-SUMMARY.md",
        "77-03-SUMMARY.md",
        "77-VERIFICATION.md",
        "77-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "78-quality-gate-formalization-route-handoff-ergonomics-and-milestone-closeout-readiness",
        "78-01-SUMMARY.md",
        "78-02-SUMMARY.md",
        "78-03-SUMMARY.md",
        "78-SUMMARY.md",
        "78-VERIFICATION.md",
        "78-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "79-governance-tooling-hotspot-decomposition-and-release-contract-topicization",
        "79-01-SUMMARY.md",
        "79-02-SUMMARY.md",
        "79-03-SUMMARY.md",
        "79-SUMMARY.md",
        "79-VERIFICATION.md",
        "79-VALIDATION.md",
    )
    _assert_promoted_phase_assets(
        "80-governance-typing-closure-and-final-meta-suite-hotspot-topicization",
        "80-01-SUMMARY.md",
        "80-02-SUMMARY.md",
        "80-03-SUMMARY.md",
        "80-SUMMARY.md",
        "80-VERIFICATION.md",
        "80-VALIDATION.md",
    )

    assert_pull_only_evidence_index(
        evidence_index,
        "76-VERIFICATION.md",
        "77-VALIDATION.md",
        "80-VERIFICATION.md",
        "archived / evidence-ready",
        "V1_21_EVIDENCE_INDEX.md",
    )
