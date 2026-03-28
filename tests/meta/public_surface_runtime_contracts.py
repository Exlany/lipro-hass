"""Runtime-facing public-surface contract guards."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.architecture_policy import load_targeted_bans, policy_root
from tests.helpers.ast_guard_utils import (
    extract_all,
    extract_property_names,
    extract_top_level_bindings,
)

_ROOT = policy_root(Path(__file__))
_PUBLIC_SURFACES = _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
_RULES = load_targeted_bans(_ROOT)


def test_phase_40_review_ledgers_keep_shared_execution_facade_out_of_residual_and_kill() -> (
    None
):
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "custom_components/lipro/services/execution.py" in file_matrix_text
    assert (
        "formal service execution facade; private auth seam closed" in file_matrix_text
    )
    assert "## Phase 40 Residual Delta" in residual_text
    assert "schedule.py" in residual_text
    assert "formal service execution facade" in residual_text
    assert "## Phase 40 Status Update" in kill_text
    assert "custom_components/lipro/services/execution.py" in kill_text


def test_legacy_protocol_exports_do_not_reexpand_root_packages() -> None:
    for rule_id in (
        "ENF-COMPAT-ROOT-NO-LEGACY-CLIENT",
        "ENF-COMPAT-CONFIG-FLOW-NO-LEGACY-CLIENT",
        "ENF-COMPAT-CORE-PACKAGE-NO-LEGACY-CLIENTS",
        "ENF-COMPAT-MQTT-PACKAGE-NO-LEGACY-CLIENT",
    ):
        rule = _RULES[rule_id]
        file_path = _ROOT / rule.governed_targets[0]
        bindings = set(extract_top_level_bindings(file_path, root=_ROOT))

        assert set(rule.allowed_or_required_signals).issubset(bindings)
        assert bindings.isdisjoint(rule.forbidden_signals)


def test_core_package_does_not_reexport_runtime_home_symbols() -> None:
    from custom_components.lipro import coordinator_entry, core

    assert not hasattr(core, "Coordinator")
    assert hasattr(coordinator_entry, "Coordinator")


def test_coordinator_runtime_surface_stays_service_oriented() -> None:
    rule = _RULES["ENF-BACKDOOR-COORDINATOR-PROPERTIES"]
    relative_path, class_name = rule.governed_targets[0].split("::", maxsplit=1)
    property_names = extract_property_names(
        _ROOT / relative_path, class_name, root=_ROOT
    )

    assert set(rule.allowed_or_required_signals).issubset(property_names)
    assert property_names.isdisjoint(rule.forbidden_signals)


def test_service_execution_uses_formal_auth_surface_instead_of_private_backdoor() -> (
    None
):
    rule = _RULES["ENF-BACKDOOR-SERVICE-AUTH"]
    file_path = _ROOT / rule.governed_targets[0]
    execution_text = file_path.read_text(encoding="utf-8")

    for signal in rule.allowed_or_required_signals:
        assert signal in execution_text
    for signal in rule.forbidden_signals:
        assert signal not in execution_text


def test_runtime_power_surface_stays_read_only_and_formalized() -> None:
    state_reader_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "coordinator"
        / "runtime"
        / "state"
        / "reader.py"
    ).read_text(encoding="utf-8")
    outlet_power_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "coordinator"
        / "outlet_power.py"
    ).read_text(encoding="utf-8")
    runtime_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "coordinator"
        / "runtime"
        / "outlet_power_runtime.py"
    ).read_text(encoding="utf-8")
    diagnostics_text = (
        _ROOT / "custom_components" / "lipro" / "control" / "diagnostics_surface.py"
    ).read_text(encoding="utf-8")
    power_service_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "power_service.py"
    ).read_text(encoding="utf-8")
    sensor_text = (_ROOT / "custom_components" / "lipro" / "sensor.py").read_text(
        encoding="utf-8"
    )
    device_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "device" / "device.py"
    ).read_text(encoding="utf-8")

    assert "MappingProxyType" in state_reader_text
    assert 'extra_data["power_info"]' not in outlet_power_text
    assert 'extra_data.get("power_info")' not in sensor_text
    assert 'extra_data.get("power_info")' not in device_text
    assert "outlet_power_info" in diagnostics_text
    assert '"data": rows' not in power_service_text
    assert '"data": rows' not in runtime_text


def test_phase_30_control_contracts_stay_private_and_system_health_minimal() -> None:
    control_exports = set(
        extract_all(
            _ROOT / "custom_components" / "lipro" / "control" / "__init__.py",
            root=_ROOT,
        )
    )
    failure_policy_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "control"
        / "entry_lifecycle_failures.py"
    ).read_text(encoding="utf-8")
    system_health_text = (
        _ROOT / "custom_components" / "lipro" / "control" / "system_health_surface.py"
    ).read_text(encoding="utf-8")

    assert "LifecycleFailureContract" not in control_exports
    for token in (
        "setup_auth_failed",
        "setup_not_ready",
        "setup_failed",
        "unload_shutdown_degraded",
        "reload_auth_failed",
        "reload_not_ready",
        "reload_failed",
    ):
        assert token in failure_policy_text

    assert "FailureEntry" in system_health_text
    assert "SystemHealthPayload" in system_health_text
    assert "Any" not in system_health_text
    assert "diagnostics" not in system_health_text
    assert "developer" not in system_health_text
    for token in (
        "RuntimeCoordinatorSnapshot",
        "iter_runtime_entries",
        "iter_runtime_coordinators",
        "build_entry_telemetry_exporter",
        "build_entry_telemetry_snapshot",
        "build_entry_telemetry_views",
        "get_entry_telemetry_exporter",
    ):
        assert token not in control_exports


def test_phase89_runtime_protocol_exposes_entity_verbs_instead_of_service_handles() -> None:
    runtime_types_text = (
        _ROOT / "custom_components" / "lipro" / "runtime_types.py"
    ).read_text(encoding="utf-8")
    runtime_protocol_block = runtime_types_text.split(
        "class LiproRuntimeCoordinator(Protocol):",
        maxsplit=1,
    )[1].split(
        "class LiproCoordinator(LiproRuntimeCoordinator, Protocol):",
        maxsplit=1,
    )[0]

    assert "async_send_command(" in runtime_protocol_block
    assert "async_apply_optimistic_state(" in runtime_protocol_block
    assert "async_query_device_ota_info(" in runtime_protocol_block
    assert "command_service" not in runtime_protocol_block
    assert "protocol_service" not in runtime_protocol_block
    assert "get_device_lock" not in runtime_protocol_block
