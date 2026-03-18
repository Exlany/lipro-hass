"""Runtime-focused governance phase-history regression coverage."""

from __future__ import annotations

from .test_governance_guards import (
    _AGENTS,
    _ROOT,
    _assert_state_preserves_phase_17_closeout_history,
)


def test_phase_30_31_typed_closeout_truth_is_consistent() -> None:
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    handoff_text = (_ROOT / ".planning" / "v1.3-HANDOFF.md").read_text(encoding="utf-8")
    validation_30_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "30-protocol-control-typed-contract-tightening"
        / "30-VALIDATION.md"
    ).read_text(encoding="utf-8")
    verification_30_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "30-protocol-control-typed-contract-tightening"
        / "30-VERIFICATION.md"
    ).read_text(encoding="utf-8")
    validation_31_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "31-runtime-service-typed-budget-and-exception-closure"
        / "31-VALIDATION.md"
    ).read_text(encoding="utf-8")
    verification_31_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "31-runtime-service-typed-budget-and-exception-closure"
        / "31-VERIFICATION.md"
    ).read_text(encoding="utf-8")

    assert "`Phase 30` 已完成：REST response/result spine" in state_text
    assert "`Phase 31` 已完成：runtime/service/platform touched zones" in state_text
    assert "setup_auth_failed/setup_not_ready/setup_failed" in handoff_text
    assert "unload_shutdown_degraded" in handoff_text
    assert "shared `failure_summary`" in handoff_text
    assert "Phase 31 只承接 runtime/service/platform typed budget" in handoff_text
    assert (
        "`tests/meta/test_phase31_runtime_budget_guards.py` 已把 `sanctioned_any`、`backlog_any`"
        in handoff_text
    )

    assert "status: passed" in validation_30_text
    assert "30-01-01" in validation_30_text and "✅ passed" in validation_30_text
    assert "30-02-01" in validation_30_text and "✅ passed" in validation_30_text
    assert "30-03-02" in validation_30_text and "✅ passed" in validation_30_text
    assert "30-VERIFICATION.md" in validation_30_text
    assert "# Phase 30 Verification" in verification_30_text
    assert "status: passed" in verification_30_text
    assert "18 passed" in verification_30_text
    assert "215 passed" in verification_30_text

    assert "status: passed" in validation_31_text
    assert "31-01-01" in validation_31_text and "✅ passed" in validation_31_text
    assert "31-04-02" in validation_31_text and "✅ passed" in validation_31_text
    assert "31-VERIFICATION.md" in validation_31_text
    assert "# Phase 31 Verification" in verification_31_text
    assert "status: passed" in verification_31_text
    assert "sanctioned_any" in verification_31_text
    assert "backlog_any" in verification_31_text
    assert "tests/meta/test_phase31_runtime_budget_guards.py" in verification_31_text


def test_execution_service_is_not_marked_as_active_runtime_auth_seam() -> None:
    agents_text = _AGENTS.read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )
    structure_text = (_ROOT / ".planning" / "codebase" / "STRUCTURE.md").read_text(
        encoding="utf-8"
    )
    architecture_text = (
        _ROOT / ".planning" / "codebase" / "ARCHITECTURE.md"
    ).read_text(encoding="utf-8")

    assert "Phase 5 已关闭 coordinator 私有 auth seam" in agents_text
    assert "仍有 coordinator 私有 auth seam" not in agents_text
    assert (
        "| `custom_components/lipro/services/execution.py` | Control | Phase 3 / 5 / 7 | 保留 | "
        "formal service execution facade; private auth seam closed |"
    ) in file_matrix_text
    assert "runtime-auth seam" not in structure_text
    assert (
        "runtime-auth seam：`custom_components/lipro/services/execution.py`"
        not in architecture_text
    )
    assert "私有 auth hook seam 已在 Phase 5 关闭" in residual_text
    assert "不再作为 active kill target" in kill_text


def test_phase_16_execution_truth_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    validation_text = (phase_root / "16-VALIDATION.md").read_text(encoding="utf-8")
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(
        encoding="utf-8"
    )
    verification_matrix_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")

    assert "### 11. Phase 16 后审计收口线已完成" in project_text
    assert (
        "| 16 Post-audit Truth Alignment, Hotspot Decomposition & Residual Endgame | v1.1 | 6/6 | Complete | 2026-03-15 |"
        in roadmap_text
    )
    assert "**Plans:** 6/6 complete across 3 waves" in roadmap_text
    for req_id in (
        "GOV-14",
        "QLT-02",
        "HOT-04",
        "TYP-04",
        "ERR-01",
        "RES-02",
        "CTRL-06",
        "DOM-03",
        "OTA-01",
        "TST-01",
        "DOC-02",
    ):
        assert f"| {req_id} | Phase 16 | Complete |" in requirements_text
    _assert_state_preserves_phase_17_closeout_history(state_text)
    assert "status: passed" in validation_text
    assert "| 16-02-00 | 16-02 | 1 | QLT-02 / DOC-02 |" in validation_text
    assert "| 16-03-00 | 16-03 | 2 | CTRL-06 / ERR-01 / TYP-04 |" in validation_text
    assert "| 16-05-00 | 16-05 | 3 | DOM-03 / OTA-01 |" in validation_text
    assert "| 16-06-00 | 16-06 | 3 | TST-01 / DOC-02 / GOV-14 |" in validation_text
    assert "本地 codebase maps" in authority_text
    assert "## Phase 16 Governance Calibration Notes" in public_text
    assert (
        "## Phase 16 Governance / Toolchain Entry Contract" in verification_matrix_text
    )
    assert "## Phase 16 Closeout Contract" in verification_matrix_text

    for artifact_name in (
        "16-PRD.md",
        "16-CONTEXT.md",
        "16-RESEARCH.md",
        "16-VALIDATION.md",
        "16-01-PLAN.md",
        "16-02-PLAN.md",
        "16-03-PLAN.md",
        "16-04-PLAN.md",
        "16-05-PLAN.md",
        "16-06-PLAN.md",
        "16-03-SUMMARY.md",
        "16-04-SUMMARY.md",
        "16-05-SUMMARY.md",
        "16-06-SUMMARY.md",
    ):
        assert (phase_root / artifact_name).exists()


def test_phase_17_execution_truth_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "17-final-residual-retirement-typed-contract-tightening-and-milestone-closeout"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(
        encoding="utf-8"
    )
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    verification_matrix_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )
    validation_text = (phase_root / "17-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "17-VERIFICATION.md").read_text(encoding="utf-8")
    audit_text = (_ROOT / ".planning" / "v1.1-MILESTONE-AUDIT.md").read_text(
        encoding="utf-8"
    )

    assert (
        "### 12. Phase 17 最终残留退役 / 类型契约收紧 / 里程碑收官已完成"
        in project_text
    )
    assert (
        "| 17 Final Residual Retirement, Typed-Contract Tightening & Milestone Closeout | v1.1 | 4/4 | Complete | 2026-03-15 |"
        in roadmap_text
    )
    assert "**Plans:** 4/4 complete" in roadmap_text
    for req_id in ("RES-03", "TYP-05", "MQT-01", "GOV-15"):
        assert f"| {req_id} | Phase 17 | Complete |" in requirements_text
    _assert_state_preserves_phase_17_closeout_history(state_text)
    assert "## Phase 17 Final Residual Retirement Notes" in public_text
    assert "auth/session snapshot contract" in authority_text
    assert "## Phase 17 Closeout Contract" in verification_matrix_text
    assert "## Phase 17 Residual Delta" in residual_text
    assert "## Phase 17 Status Update" in kill_text
    assert "status: passed" in validation_text
    assert "status: passed" in verification_text
    assert "69 / 69" in audit_text
    assert "15 / 15" in audit_text

    for artifact_name in (
        "17-CONTEXT.md",
        "17-RESEARCH.md",
        "17-01-PLAN.md",
        "17-02-PLAN.md",
        "17-03-PLAN.md",
        "17-04-PLAN.md",
        "17-01-SUMMARY.md",
        "17-02-SUMMARY.md",
        "17-03-SUMMARY.md",
        "17-04-SUMMARY.md",
        "17-VALIDATION.md",
        "17-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()


def test_phase_19_execution_truth_is_consistent() -> None:
    phase_root = (
        _ROOT / ".planning" / "phases" / "19-headless-consumer-proof-adapter-demotion"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(
        encoding="utf-8"
    )
    verification_matrix_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )
    validation_text = (phase_root / "19-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "19-VERIFICATION.md").read_text(encoding="utf-8")

    assert "## Current Milestone (v1.2)" in project_text
    assert "**Execution status:** `Phase 18-24` complete" in project_text
    assert "## Current Milestone" in roadmap_text
    assert "### Phase 19: Headless Consumer Proof & Adapter Demotion" in roadmap_text
    assert "**Requirements**: [CORE-02]" in roadmap_text
    assert "**Status**: Complete (`2026-03-16`)" in roadmap_text
    assert "**Plans**: 4/4 complete" in roadmap_text
    assert "# Requirements: Lipro-HASS" in requirements_text
    assert (
        "*Last updated: 2026-03-17 after Phase 24 reopen revalidation*"
        in requirements_text
    )
    assert "## Traceability for v1.2" in requirements_text
    assert "| CORE-02 | Phase 19 | Complete |" in requirements_text
    assert "- `Phase 24` 已完成并于 2026-03-17 重新验证" in state_text
    assert "## Phase 19 Headless Proof & Adapter Shell Notes" in public_text
    assert "## Phase 19 Headless Consumer Proof Contract" in verification_matrix_text
    assert "## Phase 19 Residual Delta" in residual_text
    assert "## Phase 19 Status Update" in kill_text
    assert "status: passed" in validation_text
    assert "status: passed" in verification_text

    for artifact_name in (
        "19-CONTEXT.md",
        "19-RESEARCH.md",
        "19-01-PLAN.md",
        "19-02-PLAN.md",
        "19-03-PLAN.md",
        "19-04-PLAN.md",
        "19-01-SUMMARY.md",
        "19-02-SUMMARY.md",
        "19-03-SUMMARY.md",
        "19-04-SUMMARY.md",
        "19-VALIDATION.md",
        "19-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()


def test_phase_22_observability_consumer_governance_truth_is_synced() -> None:
    verification_matrix_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )

    assert (
        "## Phase 22 Observability Consumer Convergence Contract"
        in verification_matrix_text
    )
    assert "复用共享 `failure_summary` vocabulary" in verification_matrix_text
    assert "custom_components/lipro/control/diagnostics_surface.py" in file_matrix_text
    assert (
        "custom_components/lipro/control/system_health_surface.py" in file_matrix_text
    )
    assert "## Phase 22 Residual Delta" in residual_text
    assert "exporter-only truth" in residual_text


def test_phase_36_execution_evidence_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "36-runtime-root-and-exception-burn-down"
    )
    validation_text = (phase_root / "36-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "36-VERIFICATION.md").read_text(encoding="utf-8")
    summary_text = (phase_root / "36-SUMMARY.md").read_text(encoding="utf-8")

    assert "status: passed" in validation_text
    assert "36-01-01" in validation_text and "✅ passed" in validation_text
    assert "# Phase 36 Verification" in verification_text
    assert "CoordinatorPollingService" in verification_text
    assert "phase: 36" in summary_text
