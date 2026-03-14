"""Governance guards for file-matrix coverage and architecture-policy hygiene."""

from __future__ import annotations

from pathlib import Path
import re

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





def _assert_current_mode_tracks_phase_lifecycle(state_text: str) -> None:
    assert re.search(
        r"\*\*Current mode:\*\* `Phase \d+(?:\.\d+)? [a-z][a-z0-9_ -]+`",
        state_text,
    )

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
        "ENF-COMPAT-ROOT-NO-LEGACY-CLIENT",
        "ENF-COMPAT-CONFIG-FLOW-NO-LEGACY-CLIENT",
        "ENF-COMPAT-CORE-PACKAGE-NO-LEGACY-CLIENTS",
        "ENF-COMPAT-MQTT-PACKAGE-NO-LEGACY-CLIENT",
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
    _assert_current_mode_tracks_phase_lifecycle(state_text)
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
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "status: passed" in validation_text
    assert "nyquist_compliant: true" in validation_text
    assert "wave_0_complete: true" in validation_text
    assert "status: passed" in verification_text



def test_phase_9_governance_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    validation_text = (_ROOT / ".planning" / "phases" / "09-residual-surface-closure" / "09-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (_ROOT / ".planning" / "phases" / "09-residual-surface-closure" / "09-VERIFICATION.md").read_text(encoding="utf-8")
    uat_text = (_ROOT / ".planning" / "phases" / "09-residual-surface-closure" / "09-UAT.md").read_text(encoding="utf-8")
    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(encoding="utf-8")
    authority_text = (_ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md").read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(encoding="utf-8")

    assert '- [x] 09-01: 收窄 protocol root surface 与 compat exports' in roadmap_text
    assert '| RSC-01 | Phase 9 | Complete |' in requirements_text
    assert '| RSC-04 | Phase 9 | Complete |' in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert 'status: passed' in validation_text
    assert 'status: passed' in verification_text
    assert '## Automated UAT Verdict' in uat_text
    assert 'core.api.LiproClient' in public_text
    assert 'LiproProtocolFacade.get_device_list' in public_text
    assert 'LiproMqttFacade.raw_client' in public_text
    assert 'runtime supplemental state primitives' in authority_text
    assert residual_text.count('## Phase 09 Residual Delta') == 1
    assert kill_text.count('## Phase 09 Status Update') == 1
    for seam in (
        'core.api.LiproClient',
        'LiproProtocolFacade.get_device_list',
        'LiproMqttFacade.raw_client',
    ):
        assert seam in residual_text
        assert seam in kill_text



def test_phase_11_replanning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    context_text = (_ROOT / ".planning" / "phases" / "11-control-router-formalization-wiring-residual-demotion" / "11-CONTEXT.md").read_text(encoding="utf-8")
    research_text = (_ROOT / ".planning" / "phases" / "11-control-router-formalization-wiring-residual-demotion" / "11-RESEARCH.md").read_text(encoding="utf-8")
    audit_text = (_ROOT / ".planning" / "v1.1-MILESTONE-AUDIT.md").read_text(encoding="utf-8")

    assert "| 11 Control Router Formalization & Wiring Residual Demotion | v1.1 | 3/8 | In Progress | 2026-03-14 |" in roadmap_text
    assert "| SURF-01 | Phase 11 | Planned |" in requirements_text
    assert "| CTRL-04 | Phase 11 | Planned |" in requirements_text
    assert "| RUN-01 | Phase 11 | Planned |" in requirements_text
    assert "| ENT-01 | Phase 11 | Planned |" in requirements_text
    assert "| ENT-02 | Phase 11 | Planned |" in requirements_text
    assert "| GOV-08 | Phase 11 | Planned |" in requirements_text
    assert "**Current mode:** `Phase 11 replanning`" in state_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "**Status:** Reopened for expanded planning" in context_text
    assert "11-04 ~ 11-08 addendum plans" in research_text
    assert "status: superseded_snapshot" in audit_text
    assert "Snapshot notice (2026-03-14)" in audit_text


def test_phase_10_governance_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    validation_text = (_ROOT / ".planning" / "phases" / "10-api-drift-isolation-core-boundary-prep" / "10-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (_ROOT / ".planning" / "phases" / "10-api-drift-isolation-core-boundary-prep" / "10-VERIFICATION.md").read_text(encoding="utf-8")
    uat_text = (_ROOT / ".planning" / "phases" / "10-api-drift-isolation-core-boundary-prep" / "10-UAT.md").read_text(encoding="utf-8")
    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(encoding="utf-8")
    dependency_text = (_ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md").read_text(encoding="utf-8")
    authority_text = (_ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md").read_text(encoding="utf-8")
    verification_matrix_text = (_ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md").read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(encoding="utf-8")

    for summary_name in (
        "10-01-SUMMARY.md",
        "10-02-SUMMARY.md",
        "10-03-SUMMARY.md",
        "10-04-SUMMARY.md",
    ):
        assert (_ROOT / ".planning" / "phases" / "10-api-drift-isolation-core-boundary-prep" / summary_name).exists()

    assert "| 10 API Drift Isolation & Core Boundary Prep | v1.1 | 4/4 | Complete | 2026-03-14 |" in roadmap_text
    assert "| ISO-01 | Phase 10 | Complete |" in requirements_text
    assert "| ISO-04 | Phase 10 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "status: passed" in validation_text
    assert "tests/meta/test_governance_guards.py" in validation_text
    assert "status: passed" in verification_text
    assert "AuthSessionSnapshot" in verification_text
    assert "## Automated UAT Verdict" in uat_text
    assert "4/4 通过" in uat_text
    assert "AuthSessionSnapshot" in public_text
    assert "`Coordinator` 不再从这里导出" in public_text
    assert "runtime_access.get_entry_runtime_coordinator()" in public_text
    assert "entry.runtime_data.coordinator" in dependency_text
    assert "rest.device-list@v1" in authority_text
    assert "rest.device-status@v1" in authority_text
    assert "rest.mesh-group-status@v1" in authority_text
    assert "AuthSessionSnapshot" in authority_text
    assert "| `ISO-*` |" in verification_matrix_text
    assert "## Phase 10 Exit Contract" in verification_matrix_text
    assert residual_text.count("## Phase 10 Residual Delta") == 1
    assert kill_text.count("## Phase 10 Status Update") == 1
    for seam in (
        "core.api.LiproClient",
        "LiproProtocolFacade.get_device_list",
        "LiproMqttFacade.raw_client",
    ):
        assert seam in residual_text
        assert seam in kill_text
