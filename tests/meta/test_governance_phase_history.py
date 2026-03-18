"""Topicized governance regression coverage extracted from `tests/meta/test_governance_guards.py` (test_governance_phase_history)."""

from __future__ import annotations

from .test_governance_guards import (
    _AGENTS,
    _ROOT,
    _assert_current_mode_tracks_phase_lifecycle,
    _assert_state_preserves_phase_17_closeout_history,
    _extract_markdown_section,
    _load_frontmatter,
)


def test_phase_7_5_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    validation_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "07.5-integration-governance-verification-closeout"
        / "07.5-VALIDATION.md"
    ).read_text(encoding="utf-8")

    assert (
        "| 7.5 Governance & Verification | v1.1 | 2/2 | Complete | 2026-03-13 |"
        in roadmap_text
    )
    assert "| GOV-06 | Phase 7.5 | Complete |" in requirements_text
    assert "| GOV-07 | Phase 7.5 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "status: passed" in validation_text
    assert "- [x] `.planning/reviews/V1_1_EVIDENCE_INDEX.md`" in validation_text
    assert (
        "- [x] All tasks have automated verify or Wave 0 dependencies"
        in validation_text
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


def test_phase_8_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    validation_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "08-ai-debug-evidence-pack"
        / "08-VALIDATION.md"
    ).read_text(encoding="utf-8")
    verification_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "08-ai-debug-evidence-pack"
        / "08-VERIFICATION.md"
    ).read_text(encoding="utf-8")

    assert (
        "| 8 AI Debug Evidence Pack | v1.1 | 2/2 | Complete | 2026-03-13 |"
        in roadmap_text
    )
    assert "| AID-01 | Phase 8 | Complete |" in requirements_text
    assert "| AID-02 | Phase 8 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "status: passed" in validation_text
    assert "nyquist_compliant: true" in validation_text
    assert "wave_0_complete: true" in validation_text
    assert "status: passed" in verification_text


def test_phase_9_governance_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    validation_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "09-residual-surface-closure"
        / "09-VALIDATION.md"
    ).read_text(encoding="utf-8")
    verification_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "09-residual-surface-closure"
        / "09-VERIFICATION.md"
    ).read_text(encoding="utf-8")
    uat_text = (
        _ROOT / ".planning" / "phases" / "09-residual-surface-closure" / "09-UAT.md"
    ).read_text(encoding="utf-8")
    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(
        encoding="utf-8"
    )
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "- [x] 09-01: 收窄 protocol root surface 与 compat exports" in roadmap_text
    assert "| RSC-01 | Phase 9 | Complete |" in requirements_text
    assert "| RSC-04 | Phase 9 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "status: passed" in validation_text
    assert "status: passed" in verification_text
    assert "## Automated UAT Verdict" in uat_text
    assert "services/wiring.py" not in public_text
    assert "runtime device registry read surface" in authority_text
    assert "outlet power primitive" in authority_text
    assert residual_text.count("## Phase 09 Residual Delta") == 1
    assert kill_text.count("## Phase 09 Status Update") == 1
    for seam in (
        "core.api.LiproClient",
        "LiproProtocolFacade.get_device_list",
        "LiproMqttFacade.raw_client",
    ):
        assert seam in residual_text
        assert seam in kill_text


def test_phase_11_execution_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(
        encoding="utf-8"
    )
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    research_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "11-control-router-formalization-wiring-residual-demotion"
        / "11-RESEARCH.md"
    ).read_text(encoding="utf-8")
    audit_frontmatter = _load_frontmatter(
        _ROOT / ".planning" / "v1.1-MILESTONE-AUDIT.md"
    )

    assert (
        "| 11 Control Router Formalization & Wiring Residual Demotion | v1.1 | 8/8 | Complete | 2026-03-14 |"
        in roadmap_text
    )
    assert "| SURF-01 | Phase 11 | Complete |" in requirements_text
    assert "| CTRL-04 | Phase 11 | Complete |" in requirements_text
    assert "| RUN-01 | Phase 11 | Complete |" in requirements_text
    assert "| ENT-01 | Phase 11 | Complete |" in requirements_text
    assert "| ENT-02 | Phase 11 | Complete |" in requirements_text
    assert "| GOV-08 | Phase 11 | Complete |" in requirements_text
    assert "services/wiring.py" not in public_text
    assert "custom_components/lipro/services/wiring.py" not in file_matrix_text
    assert "11-04 ~ 11-08 addendum plans" in research_text
    assert audit_frontmatter["status"] in {"superseded_snapshot", "tech_debt"}
    scores = audit_frontmatter["scores"]
    assert isinstance(scores, dict)
    assert scores["requirements"] in {"30/30", "65/65", "69/69"}
    if audit_frontmatter["status"] == "superseded_snapshot":
        assert audit_frontmatter["snapshot_scope"] == "phase_11_complete_pre_closeout"


def test_phase_15_execution_truth_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through"
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
    architecture_policy_text = (
        _ROOT / ".planning" / "baseline" / "ARCHITECTURE_POLICY.md"
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
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    prd_text = (phase_root / "15-PRD.md").read_text(encoding="utf-8")
    context_text = (phase_root / "15-CONTEXT.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "15-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "15-VERIFICATION.md").read_text(encoding="utf-8")

    assert (
        "### 10. Phase 15 支持反馈契约 / 治理真源修补 / 可维护性跟进已完成"
        in project_text
    )
    assert (
        "| 15 Support Feedback Contract Hardening, Governance Truth Repair & Maintainability Follow-Through | v1.1 | 5/5 | Complete | 2026-03-15 |"
        in roadmap_text
    )
    assert (
        "**Requirements**: [SPT-01, GOV-13, DOC-01, HOT-03, QLT-01, TYP-03, RES-01]"
        in roadmap_text
    )
    for req_id in (
        "SPT-01",
        "GOV-13",
        "DOC-01",
        "HOT-03",
        "QLT-01",
        "TYP-03",
        "RES-01",
    ):
        assert f"| {req_id} | Phase 15 | Complete |" in requirements_text
    _assert_state_preserves_phase_17_closeout_history(state_text)
    assert "2026.3.1" in prd_text
    assert "2026.3.1" in context_text
    assert "status: passed" in validation_text
    assert "status: passed" in verification_text
    assert "## Phase 15 Surface Closure Notes" in public_text
    assert "## Phase 15 Exit Contract" in verification_matrix_text
    assert "## Phase 15 Residual Delta" in residual_text
    assert "## Phase 15 Status Update" in kill_text
    assert "## Phase 15 Policy Follow-Through" in architecture_policy_text
    assert "custom_components/lipro/core/api/client_base.py" in file_matrix_text
    assert "ClientSessionState formal REST session-state home" in file_matrix_text
    assert "custom_components/lipro/core/mqtt/mqtt_client.py" in file_matrix_text
    assert (
        "direct transport residual; locality limited to core/mqtt + protocol seam"
        in file_matrix_text
    )

    for artifact_name in (
        "15-01-PLAN.md",
        "15-02-PLAN.md",
        "15-03-PLAN.md",
        "15-04-PLAN.md",
        "15-05-PLAN.md",
        "15-01-SUMMARY.md",
        "15-02-SUMMARY.md",
        "15-03-SUMMARY.md",
        "15-04-SUMMARY.md",
        "15-05-SUMMARY.md",
        "15-VALIDATION.md",
        "15-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()


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


def test_phase_21_to_24_execution_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")

    for heading in (
        "### Phase 21: Replay Coverage & Exception Taxonomy Hardening",
        "### Phase 22: Observability Surface Convergence & Signal Exposure",
        "### Phase 23: Governance convergence, contributor docs and release evidence closure",
        "### Phase 24: Final milestone audit, archive readiness and v1.3 handoff prep",
    ):
        assert heading in roadmap_text
    assert roadmap_text.count("**Status**: Complete (`2026-03-16`)") >= 3
    assert (
        "**Status**: Complete (`2026-03-17`, revalidated after reopen)" in roadmap_text
    )
    assert "**Plans**: 5/5 complete" in roadmap_text

    for req_id in ("SIM-04", "ERR-02", "OBS-03", "GOV-16", "GOV-17", "GOV-18"):
        assert f"| {req_id} | Phase" in requirements_text
        assert (
            f"| {req_id} | Phase" in requirements_text
            and "| Complete |" in requirements_text
        )
    assert "completed_phases: 7" in state_text
    assert "completed_plans: 24" in state_text
    assert "- `Phase 24` 已完成并于 2026-03-17 重新验证" in state_text
    assert "**Execution status:** `Phase 18-24` complete" in project_text
    assert "archive-ready / `v1.3` handoff-ready" in project_text

    assert (_ROOT / ".planning" / "phases" / "21-24-v1.2-closeout-strategy.md").exists()
    for artifact in (
        _ROOT / ".planning" / "reviews" / "V1_2_EVIDENCE_INDEX.md",
        _ROOT / ".planning" / "v1.2-MILESTONE-AUDIT.md",
        _ROOT / ".planning" / "v1.3-HANDOFF.md",
    ):
        assert artifact.exists()

    expected = {
        "21-replay-exception-taxonomy-hardening": [
            "21-CONTEXT.md",
            "21-RESEARCH.md",
            "21-VALIDATION.md",
            "21-01-PLAN.md",
            "21-02-PLAN.md",
            "21-03-PLAN.md",
            "21-01-SUMMARY.md",
            "21-02-SUMMARY.md",
            "21-03-SUMMARY.md",
            "21-VERIFICATION.md",
        ],
        "22-observability-surface-convergence-and-signal-exposure": [
            "22-CONTEXT.md",
            "22-RESEARCH.md",
            "22-VALIDATION.md",
            "22-01-PLAN.md",
            "22-02-PLAN.md",
            "22-03-PLAN.md",
            "22-01-SUMMARY.md",
            "22-02-SUMMARY.md",
            "22-03-SUMMARY.md",
            "22-VERIFICATION.md",
        ],
        "23-governance-convergence-contributor-docs-and-release-evidence-closure": [
            "23-CONTEXT.md",
            "23-RESEARCH.md",
            "23-VALIDATION.md",
            "23-01-PLAN.md",
            "23-02-PLAN.md",
            "23-03-PLAN.md",
            "23-04-PLAN.md",
            "23-05-PLAN.md",
            "23-06-PLAN.md",
            "23-07-PLAN.md",
            "23-08-PLAN.md",
            "23-01-SUMMARY.md",
            "23-02-SUMMARY.md",
            "23-03-SUMMARY.md",
            "23-04-SUMMARY.md",
            "23-05-SUMMARY.md",
            "23-06-SUMMARY.md",
            "23-07-SUMMARY.md",
            "23-08-SUMMARY.md",
            "23-AUDIT-CHECKLIST.md",
            "23-VERIFICATION.md",
        ],
        "24-final-milestone-audit-archive-readiness-and-v1-3-handoff-prep": [
            "24-CONTEXT.md",
            "24-RESEARCH.md",
            "24-VALIDATION.md",
            "24-01-PLAN.md",
            "24-02-PLAN.md",
            "24-03-PLAN.md",
            "24-01-SUMMARY.md",
            "24-02-SUMMARY.md",
            "24-03-SUMMARY.md",
            "24-VERIFICATION.md",
        ],
    }
    for phase_dir, artifacts in expected.items():
        phase_root = _ROOT / ".planning" / "phases" / phase_dir
        for artifact_name in artifacts:
            assert (phase_root / artifact_name).exists()


def test_phase_20_execution_truth_is_consistent() -> None:
    phase_root = (
        _ROOT / ".planning" / "phases" / "20-remaining-boundary-family-completion"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    verification_text = (phase_root / "20-VERIFICATION.md").read_text(encoding="utf-8")

    assert "**Execution status:** `Phase 18-24` complete" in project_text
    assert "### Phase 20: Remaining Boundary Family Completion" in roadmap_text
    assert "**Status**: Complete (`2026-03-16`)" in roadmap_text
    assert "**Plans**: 3/3 complete" in roadmap_text
    assert "- [x] **SIM-03**" in requirements_text
    assert "- [x] **SIM-05**" in requirements_text
    assert "| SIM-03 | Phase 20 | Complete |" in requirements_text
    assert "| SIM-05 | Phase 20 | Complete |" in requirements_text
    assert "- `Phase 24` 已完成并于 2026-03-17 重新验证" in state_text
    assert "status: passed" in verification_text

    for artifact_name in (
        "20-CONTEXT.md",
        "20-RESEARCH.md",
        "20-VALIDATION.md",
        "20-01-PLAN.md",
        "20-02-PLAN.md",
        "20-03-PLAN.md",
        "20-01-SUMMARY.md",
        "20-02-SUMMARY.md",
        "20-03-SUMMARY.md",
        "20-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()


def test_phase_14_execution_truth_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "14-legacy-stack-final-closure-api-spine-demolition-governance-truth-consolidation"
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
    architecture_policy_text = (
        _ROOT / ".planning" / "baseline" / "ARCHITECTURE_POLICY.md"
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
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    structure_text = (_ROOT / ".planning" / "codebase" / "STRUCTURE.md").read_text(
        encoding="utf-8"
    )
    research_text = (phase_root / "14-RESEARCH.md").read_text(encoding="utf-8")
    prd_text = (phase_root / "14-PRD.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "14-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "14-VERIFICATION.md").read_text(encoding="utf-8")

    assert "### 9. Phase 14 旧 API Spine 终局收口与治理真源归一已完成" in project_text
    assert (
        "| 14 Legacy Stack Final Closure, API Spine Demolition & Governance Truth Consolidation | v1.1 | 4/4 | Complete | 2026-03-15 |"
        in roadmap_text
    )
    assert "**Requirements**: RUN-04, HOT-02, CTRL-05, RUN-05, GOV-12" in roadmap_text
    assert "| RUN-04 | Phase 14 | Complete |" in requirements_text
    assert "| GOV-12 | Phase 14 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "CoordinatorProtocolService" in prd_text
    assert "4 plans / 3 waves" in research_text
    assert "status: passed" in validation_text
    assert "status: passed" in verification_text
    assert "## Phase 14 Surface Closure Notes" in public_text
    assert "## Phase 14 Exit Contract" in verification_matrix_text
    assert "## Phase 14 Residual Delta" in residual_text
    assert "## Phase 14 Status Update" in kill_text
    assert "ENF-IMP-API-LEGACY-SPINE-LOCALITY" in architecture_policy_text
    assert "ENF-GOV-RELEASE-CI-REUSE" in architecture_policy_text
    assert (
        "custom_components/lipro/control/developer_router_support.py"
        in file_matrix_text
    )
    assert "custom_components/lipro/core/api/status_fallback.py" in file_matrix_text
    assert (
        "custom_components/lipro/core/coordinator/services/protocol_service.py"
        in file_matrix_text
    )
    assert "client.py              # compat shell" not in structure_text
    assert "LiproMqttClient compat shell" not in public_text

    for artifact_name in (
        "14-01-PLAN.md",
        "14-02-PLAN.md",
        "14-03-PLAN.md",
        "14-04-PLAN.md",
        "14-01-SUMMARY.md",
        "14-02-SUMMARY.md",
        "14-03-SUMMARY.md",
        "14-04-SUMMARY.md",
        "14-VALIDATION.md",
        "14-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()


def test_phase_13_execution_truth_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "13-explicit-domain-surface-governance-guard-hardening-hotspot-boundary-decomposition"
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
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    research_text = (phase_root / "13-RESEARCH.md").read_text(encoding="utf-8")
    prd_text = (phase_root / "13-PRD.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "13-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "13-VERIFICATION.md").read_text(encoding="utf-8")

    assert (
        "### 8. Phase 13 显式领域表面 / 治理守卫 / 热点边界收口已完成" in project_text
    )
    assert (
        "| 13 Explicit Domain Surface, Governance Guard Hardening & Hotspot Boundary Decomposition | v1.1 | 3/3 | Complete | 2026-03-14 |"
        in roadmap_text
    )
    assert "| DOM-01 | Phase 13 | Complete |" in requirements_text
    assert "| GOV-11 | Phase 13 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "`__getattr__`" in prd_text
    assert "3 plans / 2 waves" in research_text
    assert "status: passed" in validation_text
    assert "status: passed" in verification_text
    assert "device_delegation.py" not in file_matrix_text
    assert "Domain dynamic delegation" in residual_text
    assert "## Phase 13 Residual Delta" in residual_text
    assert "## Phase 13 Status Update" in kill_text
    assert "CapabilityRegistry" in public_text
    assert "动态 `__getattr__` 不再合法化" in public_text


def test_phase_12_execution_truth_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "12-type-contract-alignment-residual-cleanup-and-governance-hygiene"
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
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )
    research_text = (phase_root / "12-RESEARCH.md").read_text(encoding="utf-8")
    prd_text = (phase_root / "12-PRD.md").read_text(encoding="utf-8")

    assert any(
        status in project_text
        for status in ("**Status:** Active", "**Status:** Complete")
    )
    assert "### 7. Phase 12 Type / Residual / Governance 收口已完成" in project_text
    assert (
        "| 12 Type Contract Alignment, Residual Cleanup & Governance Hygiene | v1.1 | 5/5 | Complete | 2026-03-14 |"
        in roadmap_text
    )
    assert (
        "**Requirements**: TYP-01, TYP-02, CMP-01, CMP-02, HOT-01, GOV-09, GOV-10"
        in roadmap_text
    )
    assert "| TYP-01 | Phase 12 | Complete |" in requirements_text
    assert "| GOV-10 | Phase 12 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "Already Fixed / Must Not Be Replanned" in prd_text
    assert "5 plans / 3 waves" in research_text
    active_residual_text = _extract_markdown_section(
        residual_text, "Active Residual Families"
    )
    assert "`DeviceCapabilities` compat alias" in public_text
    assert "`core.api.LiproClient` compat shell 已在 Phase 12 正式删除" in public_text
    assert "## Phase 12 Residual Delta" in residual_text
    assert "## Phase 12 Status Update" in kill_text
    assert "`core.api.LiproClient` compat shell 已在 Phase 12 正式删除" in public_text
    assert "LiproProtocolFacade.get_device_list" in residual_text
    assert "LiproMqttFacade.raw_client" in kill_text
    assert "`DeviceCapabilities` compat alias" in public_text
    assert "已关闭（Phase 12：compat shell removed）" in kill_text
    assert "已关闭（Phase 12：compat seam removed）" in kill_text
    assert "已关闭（Phase 12：compat alias removed）" in kill_text
    for seam in (
        "core.api.LiproClient",
        "LiproProtocolFacade.get_device_list",
        "LiproMqttFacade.raw_client",
        "DeviceCapabilities",
    ):
        assert seam in kill_text or seam in public_text
        assert seam in kill_text
        assert seam not in active_residual_text
    for artifact_name in (
        "12-01-PLAN.md",
        "12-02-PLAN.md",
        "12-03-PLAN.md",
        "12-04-PLAN.md",
        "12-05-PLAN.md",
        "12-01-SUMMARY.md",
        "12-02-SUMMARY.md",
        "12-03-SUMMARY.md",
        "12-04-SUMMARY.md",
        "12-05-SUMMARY.md",
        "12-VALIDATION.md",
        "12-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()


def test_phase_10_governance_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")

    validation_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "10-api-drift-isolation-core-boundary-prep"
        / "10-VALIDATION.md"
    ).read_text(encoding="utf-8")
    verification_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "10-api-drift-isolation-core-boundary-prep"
        / "10-VERIFICATION.md"
    ).read_text(encoding="utf-8")
    uat_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "10-api-drift-isolation-core-boundary-prep"
        / "10-UAT.md"
    ).read_text(encoding="utf-8")
    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(
        encoding="utf-8"
    )
    dependency_text = (
        _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
    ).read_text(encoding="utf-8")
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

    for summary_name in (
        "10-01-SUMMARY.md",
        "10-02-SUMMARY.md",
        "10-03-SUMMARY.md",
        "10-04-SUMMARY.md",
    ):
        assert (
            _ROOT
            / ".planning"
            / "phases"
            / "10-api-drift-isolation-core-boundary-prep"
            / summary_name
        ).exists()

    assert (
        "| 10 API Drift Isolation & Core Boundary Prep | v1.1 | 4/4 | Complete | 2026-03-14 |"
        in roadmap_text
    )
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
    assert "protocol boundary decoder families" in authority_text
    assert "auth/session snapshot contract" in authority_text
    assert "AuthSessionSnapshot" in authority_text
    assert (
        "`AuthSessionSnapshot` 成为唯一正式 auth/session truth"
        in verification_matrix_text
    )
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


def test_closed_service_execution_seam_is_not_active_governance_truth() -> None:
    agents_text = (_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    architecture_text = (
        _ROOT / ".planning" / "codebase" / "ARCHITECTURE.md"
    ).read_text(encoding="utf-8")
    structure_text = (_ROOT / ".planning" / "codebase" / "STRUCTURE.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "仍有 coordinator 私有 auth seam" not in agents_text
    assert (
        "formal service execution facade; private auth seam closed" in file_matrix_text
    )
    assert (
        "runtime-auth seam：`custom_components/lipro/services/execution.py`"
        not in architecture_text
    )
    assert "过渡性 runtime-auth seam" not in structure_text
    assert "Private runtime auth seam" in residual_text
    assert "active kill target" in kill_text


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


def test_phase_34_execution_evidence_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "34-continuity-and-hard-release-gates"
    )
    validation_text = (phase_root / "34-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "34-VERIFICATION.md").read_text(encoding="utf-8")
    summary_text = (phase_root / "34-SUMMARY.md").read_text(encoding="utf-8")

    assert "status: passed" in validation_text
    assert "nyquist_compliant: true" in validation_text
    assert "34-01-01" in validation_text and "✅ passed" in validation_text
    assert "34-02-01" in validation_text and "✅ passed" in validation_text
    assert "34-03-01" in validation_text and "✅ passed" in validation_text
    assert "**Approval:** complete" in validation_text

    assert "# Phase 34 Verification" in verification_text
    assert "status: passed" in verification_text
    assert "GOV-29" in verification_text
    assert "QLT-08" in verification_text
    assert "tagged `CodeQL` gate" in verification_text
    assert "cosign" in verification_text

    assert "phase: 34" in summary_text
    assert "status: passed" in summary_text
    assert "`34-01`" in summary_text
    assert "`34-02`" in summary_text
    assert "`34-03`" in summary_text
