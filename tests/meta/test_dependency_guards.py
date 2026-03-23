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
    governed_paths, missing_governed = resolve_policy_paths(
        rule.governed_targets, root=_ROOT
    )
    allowed_paths, missing_allowed = resolve_policy_paths(
        rule.allowed_or_required_signals,
        root=_ROOT,
    )

    missing = [
        *[
            f"{rule_id} unresolved governed path pattern: {pattern}"
            for pattern in missing_governed
        ],
        *[
            f"{rule_id} unresolved allowed path pattern: {pattern}"
            for pattern in missing_allowed
        ],
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


def test_mqtt_transport_imports_stay_localized_to_protocol_and_transport_modules() -> (
    None
):
    assert not _violations_for_rule("ENF-IMP-MQTT-TRANSPORT-LOCALITY")


def test_headless_proof_boot_stays_out_of_host_runtime_and_control_planes() -> None:
    assert not _violations_for_rule("ENF-IMP-HEADLESS-PROOF-LOCALITY")


def test_platform_setup_shells_do_not_import_control_runtime_locator() -> None:
    assert not _violations_for_rule("ENF-IMP-PLATFORM-SHELL-NO-CONTROL-LOCATOR")


def test_phase_40_schedule_services_reuse_shared_execution_contract() -> None:
    schedule_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "schedule.py"
    ).read_text(encoding="utf-8")

    assert "from .execution import" in schedule_text
    assert ("AuthenticatedCoordinator" in schedule_text) or ("LiproCoordinator" in schedule_text)
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
    registrations_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "registrations.py"
    ).read_text(encoding="utf-8")
    diagnostics_helpers_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "diagnostics" / "helpers.py"
    ).read_text(encoding="utf-8")
    diagnostics_feedback_handlers_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "diagnostics" / "feedback_handlers.py"
    ).read_text(encoding="utf-8")
    control_service_registry_text = (
        _ROOT / "custom_components" / "lipro" / "control" / "service_registry.py"
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
    assert "control.runtime_access" not in maintenance_text
    assert "device_registry_updated" not in maintenance_text
    assert "async_setup_device_registry_listener" not in maintenance_text

    assert "control.service_registry" in registrations_text
    assert "control.service_router" not in registrations_text
    assert "control.runtime_access" not in diagnostics_helpers_text
    assert "import_module(" not in diagnostics_helpers_text
    assert "control.runtime_access" not in diagnostics_feedback_handlers_text
    assert "import_module(" not in diagnostics_feedback_handlers_text
    assert "PUBLIC_SERVICE_REGISTRATIONS" in control_service_registry_text
    assert "SERVICE_REGISTRATIONS" in control_service_registry_text

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


def test_phase_50_diagnostics_helpers_reuse_shared_execution_auth_chain() -> None:
    helpers_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "services"
        / "diagnostics"
        / "helpers.py"
    ).read_text(encoding="utf-8")
    helper_support_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "services"
        / "diagnostics"
        / "helper_support.py"
    ).read_text(encoding="utf-8")
    execution_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "execution.py"
    ).read_text(encoding="utf-8")

    assert "async_execute_coordinator_call" in helpers_text
    assert "async_capture_coordinator_call" not in helpers_text
    assert "async_capture_coordinator_call" in helper_support_text
    assert "auth_service.async_ensure_authenticated()" not in helpers_text
    assert "auth_service.async_trigger_reauth(" not in helpers_text
    assert "async_capture_coordinator_call" in execution_text
    assert "async_execute_coordinator_call" in execution_text


def test_phase_53_dependency_story_keeps_runtime_and_entry_support_helpers_internal() -> (
    None
):
    dependency_text = (
        _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
    ).read_text(encoding="utf-8")
    runtime_wiring_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "coordinator"
        / "runtime_wiring.py"
    ).read_text(encoding="utf-8")
    lifecycle_support_text = (
        _ROOT / "custom_components" / "lipro" / "control" / "entry_lifecycle_support.py"
    ).read_text(encoding="utf-8")
    entry_root_wiring_text = (
        _ROOT / "custom_components" / "lipro" / "control" / "entry_root_wiring.py"
    ).read_text(encoding="utf-8")

    assert "## Phase 53 Runtime / Entry-Root Clarifications" in dependency_text
    assert "runtime_wiring.py" in dependency_text
    assert "entry_lifecycle_support.py" in dependency_text
    assert "entry_root_wiring.py" in dependency_text
    assert "support-only" in runtime_wiring_text.lower()
    assert "support-only" in lifecycle_support_text.lower()
    assert "support-only" in entry_root_wiring_text.lower()


def test_phase_52_request_policy_and_protocol_root_dependency_story_is_explicit() -> (
    None
):
    dependency_text = (
        _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
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
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "protocol"
        / "protocol_facade_rest_methods.py"
    ).read_text(encoding="utf-8")

    assert (
        "## Phase 52 Request-Policy / Protocol-Root Clarifications" in dependency_text
    )
    assert "protocol_facade_rest_methods.py" in dependency_text
    assert "RequestPolicy" in dependency_text
    assert "RestRequestGateway" in dependency_text
    assert "RestTransportExecutor" in dependency_text
    assert "explicit policy-owned pacing" in request_policy_text
    assert "localized collaborator, not a second" in request_gateway_text
    assert "policy-owned 429 decisions" in transport_executor_text
    assert "policy-owned rate-limit decisions" in transport_retry_text
    assert (
        "support-only rest child-facing method surface"
        in protocol_rest_methods_text.lower()
    )
    assert "compute_exponential_retry_wait_time()" in residual_text


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


def test_phase_57_typed_command_result_dependency_story_is_explicit() -> None:
    dependency_text = (
        _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    result_policy_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "command" / "result_policy.py"
    ).read_text(encoding="utf-8")
    result_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "command" / "result.py"
    ).read_text(encoding="utf-8")
    sender_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "coordinator"
        / "runtime"
        / "command"
        / "sender.py"
    ).read_text(encoding="utf-8")
    diagnostics_types_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "diagnostics" / "types.py"
    ).read_text(encoding="utf-8")

    assert "## Phase 57 Typed Command-Result Contract Clarifications" in dependency_text
    assert "result_policy.py` 与 `custom_components/lipro/core/command/result.py` 共同组成 command-result formal contract family" in dependency_text
    assert "sender.py` 只能经 `custom_components/lipro/core/command/result.py` 读取 shared typed command-result contract" in dependency_text
    assert "Command-result stringly-typed outcome contract" in residual_text
    assert "已在 Phase 57 关闭" in residual_text
    assert "is_terminal_command_result_state" in result_policy_text
    assert "COMMAND_VERIFICATION_RESULT_TIMEOUT" in result_text
    assert "COMMAND_VERIFICATION_RESULT_TIMEOUT" in sender_text
    assert "CommandResultPollingState" in diagnostics_types_text


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
