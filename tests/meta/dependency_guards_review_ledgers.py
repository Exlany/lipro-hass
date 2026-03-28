"""Dependency-note, verification, and naming guard families."""
from __future__ import annotations

from .dependency_guard_helpers import _DEPENDENCY_MATRIX, _ROOT


def test_phase_48_dependency_notes_capture_support_only_helper_and_update_cycle() -> (
    None
):
    dependency_text = (
        _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
    ).read_text(encoding="utf-8")

    assert "## Phase 48 Formal-Root Decomposition Clarifications" in dependency_text
    assert "runtime_access_support.py" in dependency_text
    assert "build_entry_telemetry_exporter()" in dependency_text
    assert "CoordinatorUpdateCycle" in dependency_text
    assert "lazy alias seam" in dependency_text

def test_phase_49_verification_matrix_tracks_topicized_runtime_and_diagnostics_proof() -> (
    None
):
    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")

    assert (
        "## Phase 49 Mega-Test Topicization and Failure Localization Hardening"
        in verification_text
    )
    assert "tests/core/test_coordinator_entry.py" in verification_text
    assert "tests/core/test_diagnostics*.py" in verification_text
    assert "tests/meta/test_governance_promoted_phase_assets.py" in verification_text
    assert "tests/platforms/test_update_entity_refresh.py" in verification_text
    assert "tests/platforms/test_update_install_flow.py" in verification_text
    assert "tests/test_coordinator_public.py" not in verification_text
    assert "tests/test_coordinator_runtime.py" not in verification_text

def test_phase_54_helper_hotspot_dependency_story_is_explicit() -> None:
    dependency_text = (
        _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
    ).read_text(encoding="utf-8")
    manager_support_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "anonymous_share"
        / "manager_support.py"
    ).read_text(encoding="utf-8")
    share_client_support_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "anonymous_share"
        / "share_client_support.py"
    ).read_text(encoding="utf-8")
    helper_support_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "services"
        / "diagnostics"
        / "helper_support.py"
    ).read_text(encoding="utf-8")
    request_policy_support_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "api"
        / "request_policy_support.py"
    ).read_text(encoding="utf-8")
    request_policy_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "request_policy.py"
    ).read_text(encoding="utf-8")

    assert "## Phase 54 Helper-Hotspot Clarifications" in dependency_text
    assert "manager_support.py" in dependency_text
    assert "share_client_support.py" in dependency_text
    assert "helper_support.py" in dependency_text
    assert "request_policy_support.py" in dependency_text
    assert "support-only" in manager_support_text.lower()
    assert "support-only" in share_client_support_text.lower()
    assert "support-only" in helper_support_text.lower()
    assert "support-only" in request_policy_support_text.lower()
    assert "explicit policy-owned pacing" in request_policy_text

def test_phase_55_verification_and_testing_story_are_explicit() -> None:
    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    testing_text = (_ROOT / ".planning" / "codebase" / "TESTING.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 55 Mega-Test Topicization and Typing Stratification Contract" in verification_text
    for needle in (
        "test_api_command_surface_commands.py",
        "test_api_command_surface_responses.py",
        "test_transport_runtime_lifecycle.py",
        "test_transport_runtime_subscriptions.py",
        "test_light_model_and_commands.py",
        "test_fan_entity_behavior.py",
        "test_select_models.py",
        "test_switch_behavior.py",
        "production_any",
        "production_type_ignore",
        "tests_any_non_meta",
        "meta_guard_any_literals",
        "tests_type_ignore",
    ):
        assert needle in verification_text

    for needle in (
        "production_any",
        "production_type_ignore",
        "tests_any_non_meta",
        "meta_guard_any_literals",
        "meta_support_any",
        "tests_type_ignore",
        "meta_guard_type_ignore_literals",
    ):
        assert needle in testing_text

def test_phase_56_neutral_backoff_dependency_story_is_explicit() -> None:
    dependency_text = (
        _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    request_policy_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "request_policy.py"
    ).read_text(encoding="utf-8")
    backoff_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "utils" / "backoff.py"
    ).read_text(encoding="utf-8")
    result_policy_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "command" / "result_policy.py"
    ).read_text(encoding="utf-8")
    runtime_retry_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "coordinator"
        / "runtime"
        / "command"
        / "retry.py"
    ).read_text(encoding="utf-8")
    mqtt_backoff_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "mqtt" / "setup_backoff.py"
    ).read_text(encoding="utf-8")

    assert "## Phase 56 Neutral Backoff Clarifications" in dependency_text
    assert "core/utils/backoff.py" in dependency_text
    assert "def compute_exponential_retry_wait_time" not in request_policy_text
    assert "Neutral shared exponential backoff helpers" in backoff_text
    assert "from ..utils.backoff import compute_exponential_retry_wait_time" in result_policy_text
    assert "from ....utils.backoff import compute_exponential_retry_wait_time" in runtime_retry_text
    assert "from ..utils.backoff import compute_exponential_retry_wait_time" in mqtt_backoff_text
    assert "Generic backoff helper leak" in residual_text
    assert "已在 Phase 56 关闭" in residual_text

def test_phase_58_audit_refresh_clarifies_route_without_reopening_dependency_story() -> None:
    dependency_text = _DEPENDENCY_MATRIX.read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8")
    route_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "58-repository-audit-refresh-and-next-wave-routing"
        / "58-REMEDIATION-ROADMAP.md"
    ).read_text(encoding="utf-8")

    assert "## Phase 58 Repository Audit Refresh Clarifications" in dependency_text
    assert "Phase 58` 不引入新的 dependency-direction rule" in dependency_text
    assert "本 phase **无新增 active residual family**" in residual_text
    assert "## Recommended Phase Seeds" in route_text
    assert "Phase 59" in route_text

def test_phase_62_naming_discoverability_dependency_story_is_explicit() -> None:
    dependency_text = (
        _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
    ).read_text(encoding="utf-8")
    extras_support_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "device"
        / "extras_support.py"
    ).read_text(encoding="utf-8")
    endpoint_surface_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "api"
        / "endpoint_surface.py"
    ).read_text(encoding="utf-8")
    helper_support_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "services"
        / "diagnostics"
        / "helper_support.py"
    ).read_text(encoding="utf-8")

    assert "## Phase 62 Naming / Discoverability Clarifications" in dependency_text
    assert "extras_support.py" in dependency_text
    assert "endpoint_surface.py" in dependency_text
    assert "feedback_handlers.py" in dependency_text
    assert "command_result_handlers.py" in dependency_text
    assert "capability_handlers.py" in dependency_text
    assert "DeviceExtras" in extras_support_text
    assert "Support helpers" in extras_support_text
    assert "endpoint operations collaborator" in endpoint_surface_text
    assert "support-only" in helper_support_text.lower()



def test_phase_90_hotspot_freeze_dependency_story_is_explicit() -> None:
    dependency_text = (_ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8")
    kill_list_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(encoding="utf-8")

    assert "## Phase 90 Hotspot Routing Freeze Clarifications" in dependency_text
    assert "stable import shell / home" in dependency_text
    assert "canonical REST child-façade composition home" in dependency_text
    assert "## Phase 90 Residual Delta" in residual_text
    assert "无新增 active residual family" in residual_text
    assert "owner + target phase + delete gate + evidence pointer" in residual_text
    assert "## Phase 90 Status Update" in kill_list_text
    assert "无新增 active kill target" in kill_list_text
    assert "不得再被写成 future kill target" in kill_list_text



def test_phase_91_typed_boundary_dependency_story_is_explicit() -> None:
    dependency_text = (_ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_list_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 91 Canonicalization / Typed-Boundary Clarifications" in dependency_text
    assert "runtime consumers must pull canonical rows from `LiproProtocolFacade`" in dependency_text
    assert "RuntimeTelemetrySnapshot" in dependency_text
    assert "## Phase 91 Residual Delta" in residual_text
    assert "无新增 active residual family" in residual_text
    assert "typed-boundary closure" in residual_text
    assert "## Phase 91 Status Update" in kill_list_text
    assert "无新增 active kill target" in kill_list_text
    assert "typed-boundary hardening" in kill_list_text



def test_phase_93_assurance_freeze_dependency_story_is_explicit() -> None:
    dependency_text = (_ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_list_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 93 Assurance Freeze Clarifications" in dependency_text
    assert "does not add a new dependency direction" in dependency_text
    assert "## Phase 93 Residual Delta" in residual_text
    assert "无新增 active residual family" in residual_text
    assert "quality-freeze projections" in residual_text
    assert "## Phase 93 Status Update" in kill_list_text
    assert "无新增 active kill target" in kill_list_text
    assert "assurance freeze / closeout proof" in kill_list_text
