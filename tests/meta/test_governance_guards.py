"""Governance guards for file-matrix coverage and architecture-policy hygiene."""

from __future__ import annotations

from pathlib import Path

from scripts.check_architecture_policy import (
    run_checks as run_architecture_policy_checks,
)
from scripts.check_file_matrix import (
    extract_reported_total,
    iter_python_files,
    parse_file_matrix_paths,
    repo_root,
    run_checks,
)
from tests.helpers.architecture_policy import load_structural_rules, load_targeted_bans

_ROOT = repo_root(Path(__file__))
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"


def test_file_matrix_covers_workspace_python_inventory() -> None:
    inventory = iter_python_files(_ROOT)
    matrix_text = _FILE_MATRIX.read_text(encoding="utf-8")

    assert extract_reported_total(matrix_text) == len(inventory)
    assert parse_file_matrix_paths(matrix_text) == inventory


def test_governance_checker_reports_no_drift() -> None:
    assert run_checks(_ROOT) == []


def test_architecture_policy_checker_reports_no_drift() -> None:
    assert run_architecture_policy_checks(_ROOT) == []


def test_architecture_policy_rule_inventory_is_stable() -> None:
    assert set(load_structural_rules(_ROOT)) == {
        "ENF-IMP-ENTITY-PROTOCOL-INTERNALS",
        "ENF-IMP-CONTROL-NO-BYPASS",
        "ENF-IMP-BOUNDARY-LOCALITY",
        "ENF-GOV-DEPENDENCY-POLICY-REF",
        "ENF-GOV-PUBLIC-SURFACE-POLICY-REF",
        "ENF-GOV-AUTHORITY-POLICY-REF",
        "ENF-GOV-VERIFICATION-POLICY-REF",
        "ENF-GOV-CI-FAIL-FAST",
    }
    assert set(load_targeted_bans(_ROOT)) == {
        "ENF-SURFACE-COORDINATOR-ENTRY",
        "ENF-SURFACE-API-EXPORTS",
        "ENF-SURFACE-PROTOCOL-EXPORTS",
        "ENF-BACKDOOR-COORDINATOR-PROPERTIES",
        "ENF-BACKDOOR-SERVICE-AUTH",
    }



def test_v1_1_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_1_EVIDENCE_INDEX.md"
    phase_summary = _ROOT / ".planning" / "phases" / "07.5-integration-governance-verification-closeout" / "07.5-SUMMARY.md"
    plan_01_summary = _ROOT / ".planning" / "phases" / "07.5-integration-governance-verification-closeout" / "07.5-01-SUMMARY.md"
    plan_02_summary = _ROOT / ".planning" / "phases" / "07.5-integration-governance-verification-closeout" / "07.5-02-SUMMARY.md"
    verification = _ROOT / ".planning" / "phases" / "07.5-integration-governance-verification-closeout" / "07.5-VERIFICATION.md"

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
    authority_text = (_ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md").read_text(encoding="utf-8")
    verification_text = (_ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md").read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(encoding="utf-8")

    assert "runtime telemetry exporter family" in authority_text
    assert "v1.1 closeout evidence index" in authority_text
    assert "| 7.5 |" in verification_text
    assert "V1_1_EVIDENCE_INDEX.md" in verification_text
    assert "## Phase 07.5 Residual Delta" in residual_text
    assert "de-scope" in residual_text
    assert "## Phase 07.5 Status Update" in kill_text



def test_phase_7_5_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    validation_text = (_ROOT / ".planning" / "phases" / "07.5-integration-governance-verification-closeout" / "07.5-VALIDATION.md").read_text(encoding="utf-8")

    assert "| 7.5 Governance & Verification | v1.1 | 2/2 | Complete | 2026-03-13 |" in roadmap_text
    assert "| GOV-06 | Phase 7.5 | Complete |" in requirements_text
    assert "| GOV-07 | Phase 7.5 | Complete |" in requirements_text
    assert "**Current mode:** `Phase 8 completed`" in state_text
    assert "status: passed" in validation_text
    assert "- [x] `.planning/reviews/V1_1_EVIDENCE_INDEX.md`" in validation_text
    assert "- [x] All tasks have automated verify or Wave 0 dependencies" in validation_text


def test_phase_8_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    validation_text = (_ROOT / ".planning" / "phases" / "08-ai-debug-evidence-pack" / "08-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (_ROOT / ".planning" / "phases" / "08-ai-debug-evidence-pack" / "08-VERIFICATION.md").read_text(encoding="utf-8")

    assert "| 8 AI Debug Evidence Pack | v1.1 | 2/2 | Complete | 2026-03-13 |" in roadmap_text
    assert "| AID-01 | Phase 8 | Complete |" in requirements_text
    assert "| AID-02 | Phase 8 | Complete |" in requirements_text
    assert "`Phase 8 completed`" in state_text
    assert "status: passed" in validation_text
    assert "nyquist_compliant: true" in validation_text
    assert "wave_0_complete: true" in validation_text
    assert "status: passed" in verification_text
