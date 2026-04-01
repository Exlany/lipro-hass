"""Service and runtime dependency-story guards."""

from __future__ import annotations

from .dependency_guard_helpers import _ROOT


def test_phase_40_schedule_services_reuse_shared_execution_contract() -> None:
    schedule_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "schedule.py"
    ).read_text(encoding="utf-8")

    assert "from .execution import" in schedule_text
    assert ("AuthenticatedCoordinator" in schedule_text) or (
        "LiproCoordinator" in schedule_text
    )
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
    runtime_access_text = (
        _ROOT / "custom_components" / "lipro" / "control" / "runtime_access.py"
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
    registrations_path = (
        _ROOT / "custom_components" / "lipro" / "services" / "registrations.py"
    )
    diagnostics_helpers_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "services"
        / "diagnostics"
        / "helpers.py"
    ).read_text(encoding="utf-8")
    diagnostics_feedback_handlers_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "services"
        / "diagnostics"
        / "feedback_handlers.py"
    ).read_text(encoding="utf-8")
    control_service_registry_text = (
        _ROOT / "custom_components" / "lipro" / "control" / "service_registry.py"
    ).read_text(encoding="utf-8")
    runtime_infra_text = (
        _ROOT / "custom_components" / "lipro" / "runtime_infra.py"
    ).read_text(encoding="utf-8")
    runtime_infra_device_registry_text = (
        _ROOT / "custom_components" / "lipro" / "runtime_infra_device_registry.py"
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
    assert "runtime_access_support" in runtime_access_text
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

    assert not registrations_path.exists()
    assert "control.runtime_access" not in diagnostics_helpers_text
    assert "import_module(" not in diagnostics_helpers_text
    assert "control.runtime_access" not in diagnostics_feedback_handlers_text
    assert "import_module(" not in diagnostics_feedback_handlers_text
    assert "PUBLIC_SERVICE_REGISTRATIONS" in control_service_registry_text
    assert "SERVICE_REGISTRATIONS" in control_service_registry_text

    assert "async_setup_device_registry_listener" in runtime_infra_text
    assert "runtime_infra_device_registry" in runtime_infra_text
    assert "device_registry_updated" not in runtime_infra_text
    assert "async_handle_refresh_devices" not in runtime_infra_text

    assert "device_registry_updated" in runtime_infra_device_registry_text
    assert "_schedule_reloads_for_device_update" in runtime_infra_device_registry_text
    assert "support-only" in runtime_infra_device_registry_text.lower()

    for runtime_reader_text in (
        diagnostics_text,
        telemetry_surface_text,
        system_health_surface_text,
        control_service_registry_text,
        service_router_support_text,
        device_lookup_text,
        maintenance_text,
        runtime_infra_text,
    ):
        assert ".runtime_data" not in runtime_reader_text
        assert "runtime_access_support" not in runtime_reader_text


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


def test_phase_68_dependency_notes_keep_boundary_and_inward_helpers_local() -> None:
    dependency_text = (
        _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
    ).read_text(encoding="utf-8")
    topics_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "mqtt" / "topics.py"
    ).read_text(encoding="utf-8")
    runtime_access_text = (
        _ROOT / "custom_components" / "lipro" / "control" / "runtime_access.py"
    ).read_text(encoding="utf-8")

    assert "## Phase 68 Hotspot / Docs Closeout Clarifications" in dependency_text
    assert "mqtt_decoder.py" in dependency_text
    assert "boundary-backed adapter" in dependency_text
    assert "runtime_access_support.py" in dependency_text
    assert "from ..protocol.boundary.mqtt_decoder import" in topics_text
    assert "import_module(" not in topics_text
    assert 'topic.split("/")' not in topics_text
    assert "from . import runtime_access_support as _support" in runtime_access_text
