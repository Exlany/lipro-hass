"""Execution-history topology guards for archived early phases."""

from __future__ import annotations

from .conftest import (
    _ROOT,
    _assert_current_mode_tracks_phase_lifecycle,
    _extract_markdown_section,
    _load_frontmatter,
)


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
        for status in (
            "**Status:** `v1.23 active route`",
            "**Status:** Active",
            "**Status:** Complete",
            "**Status:** Shipped and archived",
            "**Status:** No active milestone route",
        )
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

    assert "**Historical archive assets:**" in project_text
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
