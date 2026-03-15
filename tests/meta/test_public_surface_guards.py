"""Public-surface guards derived from architecture policy truth."""

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


def test_public_surface_baseline_registers_assurance_only_replay_and_evidence_surfaces() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert "tests/harness/protocol/*" in public_surfaces
    assert "V1_1_EVIDENCE_INDEX.md" in public_surfaces
    assert "pull-only evidence pointers" in public_surfaces


def test_phase_15_surface_notes_keep_support_and_residual_truth_localized() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert "## Phase 15 Surface Closure Notes" in public_surfaces
    assert "local debug view" in public_surfaces
    assert "upload projector" in public_surfaces
    assert "_ClientBase" in public_surfaces
    assert "LiproMqttClient" in public_surfaces


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
    from custom_components.lipro.core.api.client import LiproRestFacade
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
    coordinator_text = (_ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "coordinator.py").read_text(encoding="utf-8")
    outlet_power_text = (_ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "outlet_power.py").read_text(encoding="utf-8")
    diagnostics_text = (_ROOT / "custom_components" / "lipro" / "control" / "diagnostics_surface.py").read_text(encoding="utf-8")
    sensor_text = (_ROOT / "custom_components" / "lipro" / "sensor.py").read_text(encoding="utf-8")

    assert "MappingProxyType" in coordinator_text
    assert 'extra_data["power_info"]' not in outlet_power_text
    assert 'extra_data.get("power_info")' not in sensor_text
    assert "outlet_power_info" in diagnostics_text
