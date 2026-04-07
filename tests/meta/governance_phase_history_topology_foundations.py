"""Foundation and early-route phase-history topology guards."""

from __future__ import annotations

from .conftest import _ROOT, _assert_current_mode_tracks_phase_lifecycle


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
