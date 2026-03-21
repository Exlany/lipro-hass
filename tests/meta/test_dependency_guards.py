"""Architecture dependency guards derived from the baseline policy truth."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.architecture_policy import (
    load_structural_rules,
    policy_root,
    resolve_policy_paths,
)
from tests.helpers.ast_guard_utils import find_forbidden_imports

_ROOT = policy_root(Path(__file__))
_DEPENDENCY_MATRIX = _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
_RULES = load_structural_rules(_ROOT)


def _violations_for_rule(rule_id: str) -> list[str]:
    rule = _RULES[rule_id]
    governed_paths, missing_governed = resolve_policy_paths(rule.governed_targets, root=_ROOT)
    allowed_paths, missing_allowed = resolve_policy_paths(
        rule.allowed_or_required_signals,
        root=_ROOT,
    )

    missing = [
        *[f"{rule_id} unresolved governed path pattern: {pattern}" for pattern in missing_governed],
        *[f"{rule_id} unresolved allowed path pattern: {pattern}" for pattern in missing_allowed],
    ]
    if missing:
        return missing

    allowed_path_set = set(allowed_paths)
    scanned_paths = [path for path in governed_paths if path not in allowed_path_set]
    violations = find_forbidden_imports(
        scanned_paths,
        tuple(rule.forbidden_signals),
        root=_ROOT,
    )
    return [f"{rule_id}: {violation}" for violation in violations]


def test_dependency_matrix_references_architecture_policy() -> None:
    dependency_matrix = _DEPENDENCY_MATRIX.read_text(encoding="utf-8")

    assert ".planning/baseline/ARCHITECTURE_POLICY.md" in dependency_matrix
    assert "ENF-IMP-ENTITY-PROTOCOL-INTERNALS" in dependency_matrix
    assert "ENF-IMP-CONTROL-NO-BYPASS" in dependency_matrix
    assert "ENF-IMP-BOUNDARY-LOCALITY" in dependency_matrix
    assert "ENF-IMP-NUCLEUS-NO-HOMEASSISTANT-IMPORT" in dependency_matrix
    assert "ENF-IMP-NUCLEUS-NO-PLATFORM-BACKFLOW" in dependency_matrix
    assert "ENF-IMP-HEADLESS-PROOF-LOCALITY" in dependency_matrix
    assert "ENF-IMP-PLATFORM-SHELL-NO-CONTROL-LOCATOR" in dependency_matrix


def test_entity_platform_surfaces_do_not_import_protocol_internals_directly() -> None:
    assert not _violations_for_rule("ENF-IMP-ENTITY-PROTOCOL-INTERNALS")


def test_control_surfaces_do_not_bypass_runtime_public_surfaces() -> None:
    assert not _violations_for_rule("ENF-IMP-CONTROL-NO-BYPASS")


def test_boundary_decoder_package_stays_inside_protocol_plane() -> None:
    assert not _violations_for_rule("ENF-IMP-BOUNDARY-LOCALITY")


def test_host_neutral_nucleus_does_not_import_homeassistant() -> None:
    assert not _violations_for_rule("ENF-IMP-NUCLEUS-NO-HOMEASSISTANT-IMPORT")


def test_host_neutral_nucleus_does_not_depend_on_adapter_platform_projection() -> None:
    assert not _violations_for_rule("ENF-IMP-NUCLEUS-NO-PLATFORM-BACKFLOW")


def test_mqtt_transport_imports_stay_localized_to_protocol_and_transport_modules() -> None:
    assert not _violations_for_rule("ENF-IMP-MQTT-TRANSPORT-LOCALITY")


def test_headless_proof_boot_stays_out_of_host_runtime_and_control_planes() -> None:
    assert not _violations_for_rule("ENF-IMP-HEADLESS-PROOF-LOCALITY")


def test_platform_setup_shells_do_not_import_control_runtime_locator() -> None:
    assert not _violations_for_rule("ENF-IMP-PLATFORM-SHELL-NO-CONTROL-LOCATOR")


def test_phase_40_schedule_services_reuse_shared_execution_contract() -> None:
    schedule_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "schedule.py"
    ).read_text(encoding="utf-8")

    assert "from .execution import (" in schedule_text
    assert "AuthenticatedCoordinator" in schedule_text
    assert "async_execute_coordinator_call" in schedule_text
    assert "_async_execute_schedule_coordinator_call" not in schedule_text
    assert "protocol_call" in schedule_text
    assert "client_call" not in schedule_text


def test_phase_40_schedule_services_use_shared_execution_contract() -> None:
    schedule_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "schedule.py"
    ).read_text(encoding="utf-8")
    execution_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "execution.py"
    ).read_text(encoding="utf-8")

    assert "async_execute_coordinator_call" in schedule_text
    assert "_async_execute_schedule_coordinator_call" not in schedule_text
    for stale_signal in (
        "LiproAuthError",
        "LiproRefreshTokenExpiredError",
        "safe_error_placeholder",
        "async_ensure_authenticated",
        "async_trigger_reauth",
    ):
        assert stale_signal not in schedule_text
    assert "async_execute_coordinator_call" in execution_text


def test_phase_48_dependency_notes_capture_support_only_helper_and_update_cycle() -> None:
    dependency_text = (_ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md").read_text(encoding="utf-8")

    assert "## Phase 48 Formal-Root Decomposition Clarifications" in dependency_text
    assert "runtime_access_support.py" in dependency_text
    assert "build_entry_telemetry_exporter()" in dependency_text
    assert "CoordinatorUpdateCycle" in dependency_text
    assert "lazy alias seam" in dependency_text


def test_phase_43_control_service_boundary_stays_one_way_and_explicit() -> None:
    diagnostics_text = (
        _ROOT / "custom_components" / "lipro" / "control" / "diagnostics_surface.py"
    ).read_text(encoding="utf-8")
    telemetry_surface_text = (
        _ROOT / "custom_components" / "lipro" / "control" / "telemetry_surface.py"
    ).read_text(encoding="utf-8")
    system_health_surface_text = (
        _ROOT / "custom_components" / "lipro" / "control" / "system_health_surface.py"
    ).read_text(encoding="utf-8")
    control_init_text = (
        _ROOT / "custom_components" / "lipro" / "control" / "__init__.py"
    ).read_text(encoding="utf-8")
    service_router_support_text = (
        _ROOT / "custom_components" / "lipro" / "control" / "service_router_support.py"
    ).read_text(encoding="utf-8")
    device_lookup_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "device_lookup.py"
    ).read_text(encoding="utf-8")
    maintenance_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "maintenance.py"
    ).read_text(encoding="utf-8")
    runtime_infra_text = (
        _ROOT / "custom_components" / "lipro" / "runtime_infra.py"
    ).read_text(encoding="utf-8")
    dependency_text = (
        _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
    ).read_text(encoding="utf-8")

    assert "## Phase 43 Control / Service Boundary Clarifications" in dependency_text
    assert "service_router_support.py" in dependency_text
    assert "runtime_infra.py" in dependency_text

    assert "build_runtime_diagnostics_projection" in diagnostics_text
    assert "find_runtime_device_for_entry" in diagnostics_text
    assert "_get_device_from_runtime" not in diagnostics_text
    assert "get_runtime_device_mapping(coordinator).get(" not in diagnostics_text

    assert "build_entry_telemetry_exporter" in telemetry_surface_text
    assert "_build_entry_telemetry_exporter" not in telemetry_surface_text
    assert "runtime_access_support" not in telemetry_surface_text
    assert "get_entry_runtime_coordinator" not in telemetry_surface_text
    assert "build_runtime_snapshots" in system_health_surface_text
    assert "iter_runtime_entries" in system_health_surface_text
    assert "get_entry_runtime_coordinator" not in system_health_surface_text
    assert "build_entry_telemetry_exporter" not in control_init_text

    assert "resolve_device_id_from_service_call" in service_router_support_text
    assert "find_runtime_device_and_coordinator" in service_router_support_text
    assert "iter_runtime_entries" not in service_router_support_text
    assert "get_entry_runtime_coordinator" not in service_router_support_text

    assert "resolve_device_id_from_service_call" in device_lookup_text
    assert "find_runtime_device_and_coordinator" not in device_lookup_text
    assert "iter_runtime_entries" not in device_lookup_text
    assert "get_entry_runtime_coordinator" not in device_lookup_text

    assert "iter_runtime_entry_coordinators" in maintenance_text
    assert "device_registry_updated" not in maintenance_text
    assert "async_setup_device_registry_listener" not in maintenance_text

    assert "async_setup_device_registry_listener" in runtime_infra_text
    assert "device_registry_updated" in runtime_infra_text
    assert "async_handle_refresh_devices" not in runtime_infra_text

    for runtime_reader_text in (
        diagnostics_text,
        telemetry_surface_text,
        system_health_surface_text,
        service_router_support_text,
        device_lookup_text,
        maintenance_text,
        runtime_infra_text,
    ):
        assert ".runtime_data" not in runtime_reader_text



def test_phase_49_verification_matrix_tracks_topicized_runtime_and_diagnostics_proof() -> None:
    verification_text = (_ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md").read_text(encoding="utf-8")

    assert "## Phase 49 Mega-Test Topicization and Failure Localization Hardening" in verification_text
    assert "tests/core/test_coordinator_entry.py" in verification_text
    assert "tests/core/test_diagnostics*.py" in verification_text
    assert "tests/meta/test_governance_promoted_phase_assets.py" in verification_text
    assert "tests/platforms/test_update_entity_refresh.py" in verification_text
    assert "tests/platforms/test_update_install_flow.py" in verification_text
    assert "tests/test_coordinator_public.py" not in verification_text
    assert "tests/test_coordinator_runtime.py" not in verification_text

def test_phase_50_diagnostics_helpers_reuse_shared_execution_auth_chain() -> None:
    helpers_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "diagnostics" / "helpers.py"
    ).read_text(encoding="utf-8")
    execution_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "execution.py"
    ).read_text(encoding="utf-8")

    assert "async_capture_coordinator_call" in helpers_text
    assert "async_execute_coordinator_call" in helpers_text
    assert "auth_service.async_ensure_authenticated()" not in helpers_text
    assert "auth_service.async_trigger_reauth(" not in helpers_text
    assert "async_capture_coordinator_call" in execution_text
    assert "async_execute_coordinator_call" in execution_text

def test_phase_52_request_policy_and_protocol_root_dependency_story_is_explicit() -> None:
    dependency_text = (
        _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (
        _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
    ).read_text(encoding="utf-8")
    request_policy_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "request_policy.py"
    ).read_text(encoding="utf-8")
    request_gateway_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "request_gateway.py"
    ).read_text(encoding="utf-8")
    transport_executor_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "transport_executor.py"
    ).read_text(encoding="utf-8")
    transport_retry_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "transport_retry.py"
    ).read_text(encoding="utf-8")
    protocol_rest_methods_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "protocol" / "protocol_facade_rest_methods.py"
    ).read_text(encoding="utf-8")

    assert "## Phase 52 Request-Policy / Protocol-Root Clarifications" in dependency_text
    assert "protocol_facade_rest_methods.py" in dependency_text
    assert "RequestPolicy" in dependency_text
    assert "RestRequestGateway" in dependency_text
    assert "RestTransportExecutor" in dependency_text
    assert "explicit policy-owned pacing" in request_policy_text
    assert "localized collaborator, not a second" in request_gateway_text
    assert "policy-owned 429 decisions" in transport_executor_text
    assert "policy-owned rate-limit decisions" in transport_retry_text
    assert "support-only rest child-facing method surface" in protocol_rest_methods_text.lower()
    assert "compute_exponential_retry_wait_time()" in residual_text

