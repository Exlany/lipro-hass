"""Topicized thin-shell pytest collection helpers."""

from __future__ import annotations

import pathlib

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_TOPICIZED_THIN_SHELLS = {
    "tests/core/test_share_client.py": {
        "tests/core/test_share_client_primitives.py",
        "tests/core/test_share_client_refresh.py",
        "tests/core/test_share_client_submit.py",
        "tests/core/test_share_client_boundary.py",
    },
    "tests/core/api/test_api_command_surface_responses.py": {
        "tests/core/api/test_api_command_surface_responses_errors.py",
        "tests/core/api/test_api_command_surface_responses_iot.py",
        "tests/core/api/test_api_command_surface_responses_success.py",
    },
    "tests/core/api/test_api_device_surface.py": {
        "tests/core/api/test_api_device_surface_connect_status.py",
        "tests/core/api/test_api_device_surface_devices.py",
        "tests/core/api/test_api_device_surface_mesh_groups.py",
        "tests/core/api/test_api_device_surface_optional_capabilities.py",
        "tests/core/api/test_api_device_surface_outlet_power.py",
        "tests/core/api/test_api_device_surface_status.py",
    },
    "tests/core/api/test_api_status_service.py": {
        "tests/core/api/test_api_status_service_fallback.py",
        "tests/core/api/test_api_status_service_wrappers.py",
    },
    "tests/core/api/test_api_transport_and_schedule.py": {
        "tests/core/api/test_api_transport_and_schedule_close.py",
        "tests/core/api/test_api_transport_and_schedule_mqtt.py",
        "tests/core/api/test_api_transport_and_schedule_schedules.py",
        "tests/core/api/test_api_transport_and_schedule_transport_boundary.py",
    },
    "tests/core/coordinator/runtime/test_command_runtime.py": {
        "tests/core/coordinator/runtime/test_command_runtime_builder_retry.py",
        "tests/core/coordinator/runtime/test_command_runtime_sender.py",
        "tests/core/coordinator/runtime/test_command_runtime_confirmation.py",
        "tests/core/coordinator/runtime/test_command_runtime_orchestration.py",
        "tests/core/coordinator/runtime/test_command_runtime_outcome_support.py",
    },
    "tests/core/coordinator/runtime/test_mqtt_runtime.py": {
        "tests/core/coordinator/runtime/test_mqtt_runtime_connection.py",
        "tests/core/coordinator/runtime/test_mqtt_runtime_init.py",
        "tests/core/coordinator/runtime/test_mqtt_runtime_messages.py",
        "tests/core/coordinator/runtime/test_mqtt_runtime_notifications.py",
    },
    "tests/meta/test_dependency_guards.py": {
        "tests/meta/dependency_guards_policy.py",
        "tests/meta/dependency_guards_protocol_contracts.py",
        "tests/meta/dependency_guards_review_ledgers.py",
        "tests/meta/dependency_guards_service_runtime.py",
    },
    "tests/meta/test_governance_followup_route.py": {
        "tests/meta/governance_followup_route_closeouts.py",
        "tests/meta/governance_followup_route_continuation.py",
        "tests/meta/governance_followup_route_current_milestones.py",
    },
    "tests/meta/test_governance_milestone_archives.py": {
        "tests/meta/governance_milestone_archives_assets.py",
        "tests/meta/governance_milestone_archives_ordering.py",
        "tests/meta/governance_milestone_archives_truth.py",
    },
    "tests/meta/test_governance_phase_history.py": {
        "tests/meta/governance_phase_history_archive_execution.py",
        "tests/meta/governance_phase_history_current_milestones.py",
        "tests/meta/governance_phase_history_mid_closeouts.py",
    },
    "tests/meta/test_governance_phase_history_topology.py": {
        "tests/meta/governance_phase_history_topology_closeouts.py",
        "tests/meta/governance_phase_history_topology_execution.py",
        "tests/meta/governance_phase_history_topology_foundations.py",
    },
    "tests/meta/test_public_surface_guards.py": {
        "tests/meta/public_surface_architecture_policy.py",
        "tests/meta/public_surface_phase_notes.py",
        "tests/meta/public_surface_runtime_contracts.py",
    },
    "tests/meta/test_toolchain_truth.py": {
        "tests/meta/toolchain_truth_checker_paths.py",
        "tests/meta/toolchain_truth_ci_contract.py",
        "tests/meta/toolchain_truth_docs_fast_path.py",
        "tests/meta/toolchain_truth_python_stack.py",
        "tests/meta/toolchain_truth_release_contract.py",
        "tests/meta/toolchain_truth_testing_governance.py",
    },
    "tests/platforms/test_light_entity_behavior.py": {
        "tests/platforms/test_light_entity_additional_coverage.py",
        "tests/platforms/test_light_entity_commands.py",
        "tests/platforms/test_light_entity_properties.py",
    },
    "tests/platforms/test_select_behavior.py": {
        "tests/platforms/select_gear_behavior_cases.py",
        "tests/platforms/select_mapped_behavior_cases.py",
        "tests/platforms/select_setup_behavior_cases.py",
    },
    "tests/services/test_services_diagnostics.py": {
        "tests/services/test_services_diagnostics_capabilities.py",
        "tests/services/test_services_diagnostics_feedback.py",
        "tests/services/test_services_diagnostics_payloads.py",
    },
}


def _normalize_pytest_target(raw: str) -> str:
    candidate = raw.split("::", 1)[0]
    if not candidate or candidate.startswith("-"):
        return ""
    path = pathlib.Path(candidate)
    try:
        return path.resolve().relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        return candidate.lstrip("./")


def pytest_ignore_collect(collection_path: pathlib.Path, config: pytest.Config) -> bool:
    """Keep thin-shell suites runnable by path without duplicating full-suite collection."""
    try:
        relative_path = collection_path.resolve().relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        return False

    if relative_path not in _TOPICIZED_THIN_SHELLS:
        return False

    explicit_targets = {
        normalized
        for normalized in (_normalize_pytest_target(arg) for arg in config.args)
        if normalized
    }
    if relative_path not in explicit_targets:
        return True

    sibling_topics = _TOPICIZED_THIN_SHELLS[relative_path]
    return any(topic in explicit_targets for topic in sibling_topics)


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Drop thin-shell items when their topical siblings are explicitly collected together."""
    explicit_targets = {
        normalized
        for normalized in (_normalize_pytest_target(arg) for arg in config.args)
        if normalized
    }
    if not explicit_targets:
        return

    shells_to_drop = {
        shell
        for shell, topics in _TOPICIZED_THIN_SHELLS.items()
        if shell in explicit_targets
        and any(topic in explicit_targets for topic in topics)
    }
    if not shells_to_drop:
        return

    items[:] = [
        item
        for item in items
        if all(not item.nodeid.startswith(f"{shell}::") for shell in shells_to_drop)
    ]


__all__ = ["pytest_collection_modifyitems", "pytest_ignore_collect"]
