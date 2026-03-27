"""Public-surface guards derived from architecture policy truth."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.architecture_policy import load_targeted_bans, policy_root
from tests.helpers.ast_guard_utils import extract_all, extract_top_level_bindings

_ROOT = policy_root(Path(__file__))
_PUBLIC_SURFACES = _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
_RULES = load_targeted_bans(_ROOT)

_ALLOWED_SCRIPT_TEST_IMPORT_PREFIXES = {
    "scripts/export_ai_debug_evidence_pack.py": ("tests.harness.evidence_pack",),
}


def _iter_test_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
    modules: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.startswith("tests.")
        ):
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


def test_public_surface_baseline_registers_assurance_only_replay_and_evidence_surfaces() -> (
    None
):
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert "tests/harness/protocol/*" in public_surfaces
    assert "V1_1_EVIDENCE_INDEX.md" in public_surfaces
    assert "pull-only evidence pointers" in public_surfaces


def test_root_adapter_uses_runtime_types_for_runtime_coordinator_truth() -> None:
    root_adapter_text = (
        _ROOT / "custom_components" / "lipro" / "__init__.py"
    ).read_text(encoding="utf-8")
    runtime_types_text = (
        _ROOT / "custom_components" / "lipro" / "runtime_types.py"
    ).read_text(encoding="utf-8")

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
    assert (
        "`get_auth_data()` compatibility projection 已从正式路径退场" in public_surfaces
    )
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

    assert set(extract_all(file_path, root=_ROOT)) == set(
        rule.allowed_or_required_signals
    )


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


def test_protocol_root_rest_child_and_mqtt_child_do_not_reintroduce_implicit_surface_delegation() -> (
    None
):
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
