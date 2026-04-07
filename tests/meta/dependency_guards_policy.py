"""Architecture-policy structural dependency guards."""
from __future__ import annotations

from .dependency_guard_helpers import _DEPENDENCY_MATRIX, _violations_for_rule


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
