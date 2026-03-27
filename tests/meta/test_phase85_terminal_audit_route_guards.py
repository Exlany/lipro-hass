"""Focused guards for Phase 85 terminal-audit truth and routing coverage."""

from __future__ import annotations

from .conftest import _ROOT
from .governance_current_truth import CURRENT_MILESTONE_DEFAULT_NEXT, CURRENT_ROUTE


def test_phase85_terminal_audit_artifact_covers_required_areas_and_routing_columns() -> None:
    audit_text = (_ROOT / ".planning" / "reviews" / "V1_23_TERMINAL_AUDIT.md").read_text(
        encoding="utf-8"
    )

    assert "v1.23 / Phase 85" in audit_text
    assert "route next" in audit_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT not in audit_text
    for area in ("production", "tests", "tooling", "docs", "governance"):
        assert area in audit_text
    for column_token in (
        "owner",
        "exit condition",
        "evidence path",
        "verdict",
        "route",
    ):
        assert column_token in audit_text
    for routed_item in (
        "share_client.py",
        "runtime_infra.py",
        "test_api_diagnostics_service.py",
        "test_protocol_contract_matrix.py",
        "test_mqtt_runtime.py",
    ):
        assert routed_item in audit_text
    assert "| `custom_components/lipro/core/anonymous_share/share_client.py` | Medium | closed in Phase 86 |" in audit_text
    assert "| `custom_components/lipro/runtime_infra.py` | Medium | closed in Phase 86 |" in audit_text
    assert "| `tests/core/api/test_api_diagnostics_service.py` | Medium | route next | `Phase 87`" in audit_text


def test_phase85_baseline_refresh_truth_blocks_stale_topology_and_backoff_stories() -> None:
    topology_text = (_ROOT / ".planning" / "baseline" / "TARGET_TOPOLOGY.md").read_text(
        encoding="utf-8"
    )
    dependency_text = (
        _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
    ).read_text(encoding="utf-8")

    assert "RestAuthRecoveryCoordinator" in topology_text
    assert "legacy client names（`LiproClient` / `LiproMqttClient`）" in topology_text
    assert "`LiproClient` 只能作为短期 compat shell" not in topology_text
    assert "AuthSession" not in topology_text
    assert "core/utils/backoff.py" in dependency_text
    assert "compat surface 读取" not in dependency_text


def test_phase85_verification_matrix_and_closeout_truth_register_current_audit_route() -> None:
    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 85 Terminal Audit / Residual Routing" in verification_text
    assert "## Phase 87 Assurance Hotspot Decomposition / No-Regrowth Guards" in verification_text
    assert CURRENT_ROUTE in verification_text
    assert "85-terminal-audit-refresh-and-residual-routing" in verification_text
    assert "V1_23_TERMINAL_AUDIT.md" in verification_text
    assert "production / tests / tooling / docs / governance" in verification_text
    assert "owner / exit condition / evidence path" in verification_text
    assert "tests/meta/test_phase87_assurance_hotspot_guards.py" in verification_text
    assert "V1_23_TERMINAL_AUDIT.md" in state_text
    assert "tests/meta/test_phase85_terminal_audit_route_guards.py" in file_matrix_text
    assert "tests/meta/test_phase87_assurance_hotspot_guards.py" in file_matrix_text
    assert residual_text.count(
        "giant assurance carriers (`test_api_diagnostics_service.py`, `test_protocol_contract_matrix.py`, `test_mqtt_runtime.py`)"
    ) == 1
    assert "| giant assurance carriers (`test_api_diagnostics_service.py`, `test_protocol_contract_matrix.py`, `test_mqtt_runtime.py`) | Assurance | closed in Phase 87 | Phase 87 |" in residual_text
    assert "| giant assurance carriers (`test_api_diagnostics_service.py`, `test_protocol_contract_matrix.py`, `test_mqtt_runtime.py`) | Assurance | route next | Phase 87 |" not in residual_text
