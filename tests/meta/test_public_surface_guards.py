"""Public-surface guards derived from architecture policy truth."""

from __future__ import annotations

import ast
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

_ALLOWED_SCRIPT_TEST_IMPORT_PREFIXES = {
    "scripts/check_architecture_policy.py": (
        "tests.helpers.architecture_policy",
        "tests.helpers.ast_guard_utils",
    ),
    "scripts/export_ai_debug_evidence_pack.py": (
        "tests.harness.evidence_pack",
    ),
}


def _iter_test_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("tests."):
            modules.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("tests."):
                    modules.add(alias.name)
    return modules


def test_public_surface_baseline_references_architecture_policy() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert ".planning/baseline/ARCHITECTURE_POLICY.md" in public_surfaces
    assert "ENF-SURFACE-COORDINATOR-ENTRY" in public_surfaces
    assert "ENF-SURFACE-API-EXPORTS" in public_surfaces
    assert "ENF-SURFACE-PROTOCOL-EXPORTS" in public_surfaces
    assert "ENF-BACKDOOR-COORDINATOR-PROPERTIES" in public_surfaces
    assert "ENF-BACKDOOR-SERVICE-AUTH" in public_surfaces
    assert "ENF-COMPAT-ROOT-NO-LEGACY-CLIENT" in public_surfaces
    assert "ENF-COMPAT-CONFIG-FLOW-NO-LEGACY-CLIENT" in public_surfaces
    assert "ENF-COMPAT-CORE-PACKAGE-NO-LEGACY-CLIENTS" in public_surfaces
    assert "ENF-COMPAT-MQTT-PACKAGE-NO-LEGACY-CLIENT" in public_surfaces
    assert "ENF-ADAPTER-CONFIG-FLOW-USES-AUTH-PROJECTION" in public_surfaces
    assert "ENF-ADAPTER-ENTRY-AUTH-USES-BOOTSTRAP" in public_surfaces
    assert "ENF-HOSTPROJ-CATEGORIES-NO-HA-PLATFORMS" in public_surfaces
    assert "ENF-HOSTPROJ-CAPABILITY-NO-PLATFORM-FIELD" in public_surfaces
    assert "ENF-HOSTPROJ-DEVICE-VIEWS-NO-PLATFORM-PROJECTION" in public_surfaces
    assert "ENF-PROOF-HEADLESS-PACKAGE-NO-EXPORTS" in public_surfaces
    assert "ENF-PROOF-HEADLESS-BOOT-NO-SECOND-ROOT-BACKFLOW" in public_surfaces


def test_public_surface_baseline_registers_assurance_only_replay_and_evidence_surfaces() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert "tests/harness/protocol/*" in public_surfaces
    assert "V1_1_EVIDENCE_INDEX.md" in public_surfaces
    assert "pull-only evidence pointers" in public_surfaces


def test_root_adapter_uses_runtime_types_for_runtime_coordinator_truth() -> None:
    root_adapter_text = (_ROOT / "custom_components" / "lipro" / "__init__.py").read_text(encoding="utf-8")
    runtime_types_text = (_ROOT / "custom_components" / "lipro" / "runtime_types.py").read_text(encoding="utf-8")

    assert "from .runtime_types import LiproRuntimeCoordinator" in root_adapter_text
    assert "class LiproRuntimeCoordinator(Protocol):" not in root_adapter_text
    assert "class LiproRuntimeCoordinator(Protocol):" in runtime_types_text


def test_scripts_keep_tests_imports_helper_only_and_pull_only() -> None:
    actual: dict[str, set[str]] = {}
    for script_path in sorted((_ROOT / "scripts").glob("*.py")):
        imports = _iter_test_imports(script_path)
        if imports:
            actual[script_path.relative_to(_ROOT).as_posix()] = imports

    assert set(actual) == set(_ALLOWED_SCRIPT_TEST_IMPORT_PREFIXES)
    for relative_path, imports in actual.items():
        prefixes = _ALLOWED_SCRIPT_TEST_IMPORT_PREFIXES[relative_path]
        assert imports
        for module in imports:
            assert module.startswith(prefixes), (relative_path, module, prefixes)


def test_phase_15_surface_notes_keep_support_truth_localized() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert "## Phase 15 Surface Closure Notes" in public_surfaces
    assert "local debug view" in public_surfaces
    assert "upload projector" in public_surfaces
    assert "Phase 15 只完成 locality / ownership wording" in public_surfaces


def test_phase_17_surface_notes_capture_final_residual_retirement() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert "## Phase 17 Final Residual Retirement Notes" in public_surfaces
    assert "`_ClientBase` 已从 production truth 退场" in public_surfaces
    assert "`_ClientTransportMixin` 已退场" in public_surfaces
    assert "`MqttTransport` 是 canonical MQTT concrete transport" in public_surfaces
    assert "`get_auth_data()` compatibility projection 已从正式路径退场" in public_surfaces
    assert 'synthetic `{"data": rows}` 已退出 formal path' in public_surfaces


def test_phase_18_surface_notes_capture_host_neutral_nucleus_alignment() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert "## Phase 18 Host-Neutral Nucleus Notes" in public_surfaces
    assert "core/auth/bootstrap.py" in public_surfaces
    assert "ConfigEntryLoginProjection" in public_surfaces
    assert "helpers/platform.py" in public_surfaces
    assert "targeted bans 阻断回流" in public_surfaces


def test_phase_19_surface_notes_capture_headless_proof_identity() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert "## Phase 19 Headless Proof & Adapter Shell Notes" in public_surfaces
    assert "local proof-only boot seam" in public_surfaces
    assert "no-export package" in public_surfaces
    assert "thin headless setup shell" in public_surfaces
    assert "ENF-PROOF-HEADLESS-PACKAGE-NO-EXPORTS" in public_surfaces


def test_coordinator_entry_exports_only_runtime_surface_symbol() -> None:
    rule = _RULES["ENF-SURFACE-COORDINATOR-ENTRY"]
    file_path = _ROOT / rule.governed_targets[0]

    assert set(extract_all(file_path, root=_ROOT)) == set(rule.allowed_or_required_signals)


def test_core_api_package_keeps_transport_internals_out_of_public_exports() -> None:
    rule = _RULES["ENF-SURFACE-API-EXPORTS"]
    file_path = _ROOT / rule.governed_targets[0]
    public_symbols = set(extract_all(file_path, root=_ROOT))

    assert set(rule.allowed_or_required_signals).issubset(public_symbols)
    assert public_symbols.isdisjoint(rule.forbidden_signals)


def test_protocol_root_keeps_boundary_decoder_exports_internal() -> None:
    rule = _RULES["ENF-SURFACE-PROTOCOL-EXPORTS"]
    file_path = _ROOT / rule.governed_targets[0]
    public_symbols = set(extract_all(file_path, root=_ROOT))

    assert set(rule.allowed_or_required_signals).issubset(public_symbols)
    assert public_symbols.isdisjoint(rule.forbidden_signals)



def test_protocol_root_rest_child_and_mqtt_child_do_not_reintroduce_implicit_surface_delegation() -> None:
    from custom_components.lipro.core.api import LiproRestFacade
    from custom_components.lipro.core.protocol.facade import (
        LiproMqttFacade,
        LiproProtocolFacade,
    )

    for facade_type in (LiproProtocolFacade, LiproRestFacade, LiproMqttFacade):
        for base in facade_type.__mro__:
            if base is object:
                continue
            assert "__getattr__" not in base.__dict__
            assert "__dir__" not in base.__dict__


def test_phase_18_adapter_and_projection_bans_keep_nucleus_host_neutral() -> None:
    for rule_id in (
        "ENF-ADAPTER-CONFIG-FLOW-USES-AUTH-PROJECTION",
        "ENF-ADAPTER-ENTRY-AUTH-USES-BOOTSTRAP",
        "ENF-HOSTPROJ-CATEGORIES-NO-HA-PLATFORMS",
        "ENF-HOSTPROJ-CAPABILITY-NO-PLATFORM-FIELD",
        "ENF-HOSTPROJ-DEVICE-VIEWS-NO-PLATFORM-PROJECTION",
    ):
        rule = _RULES[rule_id]
        file_path = _ROOT / rule.governed_targets[0]
        governed_text = file_path.read_text(encoding="utf-8")

        for signal in rule.allowed_or_required_signals:
            assert signal in governed_text
        for signal in rule.forbidden_signals:
            assert signal not in governed_text


def test_phase_19_headless_proof_bans_keep_boot_local_and_non_public() -> None:
    package_rule = _RULES["ENF-PROOF-HEADLESS-PACKAGE-NO-EXPORTS"]
    package_bindings = set(
        extract_top_level_bindings(_ROOT / package_rule.governed_targets[0], root=_ROOT)
    )

    assert set(package_rule.allowed_or_required_signals).issubset(package_bindings)
    assert package_bindings.isdisjoint(package_rule.forbidden_signals)

    boot_rule = _RULES["ENF-PROOF-HEADLESS-BOOT-NO-SECOND-ROOT-BACKFLOW"]
    boot_text = (_ROOT / boot_rule.governed_targets[0]).read_text(encoding="utf-8")
    for signal in boot_rule.allowed_or_required_signals:
        assert signal in boot_text
    for signal in boot_rule.forbidden_signals:
        assert signal not in boot_text


def test_phase_40_review_ledgers_keep_shared_execution_facade_out_of_residual_and_kill() -> None:
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(encoding="utf-8")

    assert "REST endpoint operations collaborator home" in file_matrix_text
    assert "formal service execution facade; private auth seam closed" in file_matrix_text
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
    property_names = extract_property_names(_ROOT / relative_path, class_name, root=_ROOT)

    assert set(rule.allowed_or_required_signals).issubset(property_names)
    assert property_names.isdisjoint(rule.forbidden_signals)


def test_service_execution_uses_formal_auth_surface_instead_of_private_backdoor() -> None:
    rule = _RULES["ENF-BACKDOOR-SERVICE-AUTH"]
    file_path = _ROOT / rule.governed_targets[0]
    execution_text = file_path.read_text(encoding="utf-8")

    for signal in rule.allowed_or_required_signals:
        assert signal in execution_text
    for signal in rule.forbidden_signals:
        assert signal not in execution_text


def test_runtime_power_surface_stays_read_only_and_formalized() -> None:
    state_reader_text = (_ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "runtime" / "state" / "reader.py").read_text(encoding="utf-8")
    outlet_power_text = (_ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "outlet_power.py").read_text(encoding="utf-8")
    runtime_text = (_ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "runtime" / "outlet_power_runtime.py").read_text(encoding="utf-8")
    diagnostics_text = (_ROOT / "custom_components" / "lipro" / "control" / "diagnostics_surface.py").read_text(encoding="utf-8")
    power_service_text = (_ROOT / "custom_components" / "lipro" / "core" / "api" / "power_service.py").read_text(encoding="utf-8")
    sensor_text = (_ROOT / "custom_components" / "lipro" / "sensor.py").read_text(encoding="utf-8")

    assert "MappingProxyType" in state_reader_text
    assert 'extra_data["power_info"]' not in outlet_power_text
    assert 'extra_data.get("power_info")' not in sensor_text
    assert "outlet_power_info" in diagnostics_text
    assert '"data": rows' not in power_service_text
    assert '"data": rows' not in runtime_text


def test_phase_30_control_contracts_stay_private_and_system_health_minimal() -> None:
    control_exports = set(
        extract_all(_ROOT / "custom_components" / "lipro" / "control" / "__init__.py", root=_ROOT)
    )
    failure_policy_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "control"
        / "entry_lifecycle_failures.py"
    ).read_text(encoding="utf-8")
    system_health_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "control"
        / "system_health_surface.py"
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
        "build_entry_telemetry_snapshot",
        "build_entry_telemetry_views",
        "get_entry_telemetry_exporter",
    ):
        assert token not in control_exports

def test_phase_40_public_surface_notes_capture_runtime_access_and_shared_execution() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert "## Phase 40 Governance Truth Surface Notes" in public_surfaces
    assert "GOVERNANCE_REGISTRY.json" in public_surfaces
    assert "唯一正式 read-model home" in public_surfaces
    assert "formal shared service execution facade" in public_surfaces

def test_phase_40_touched_hotspots_keep_port_protocol_and_operation_wording() -> None:
    auth_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "auth_service.py"
    ).read_text(encoding="utf-8")
    endpoint_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "endpoint_surface.py"
    ).read_text(encoding="utf-8")
    endpoint_methods_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "api"
        / "rest_facade_endpoint_methods.py"
    ).read_text(encoding="utf-8")
    snapshot_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "coordinator"
        / "runtime"
        / "device"
        / "snapshot.py"
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

    assert "AuthPort" in auth_text
    assert "AuthClient" not in auth_text
    assert "endpoint operations collaborator" in endpoint_text
    assert "forwarding" not in endpoint_text
    assert "endpoint-operation surface" in endpoint_methods_text
    assert "Forwarding lives here" not in endpoint_methods_text
    assert "SnapshotProtocolPort" in snapshot_text
    assert "SnapshotProtocolClient" not in snapshot_text
    assert "protocol: LiproProtocolFacade" in sender_text
    assert "client: LiproProtocolFacade" not in sender_text


def test_phase_40_ledgers_keep_service_execution_formal_and_non_delete_target() -> None:
    file_matrix_text = (
        _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (
        _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
    ).read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "formal service execution facade" in file_matrix_text
    assert "services/execution.py" in residual_text
    assert "formal service execution facade" in residual_text
    assert "## Phase 40 Status Update" in kill_text
    assert "formal service execution facade" in kill_text
    assert "active kill target" in kill_text

