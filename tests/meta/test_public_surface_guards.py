"""Public-surface guards derived from architecture policy truth."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.architecture_policy import load_targeted_bans, policy_root
from tests.helpers.ast_guard_utils import extract_all, extract_property_names

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
