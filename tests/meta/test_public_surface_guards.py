"""Seed public-surface guards for baseline architecture boundaries."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_PUBLIC_SURFACES = _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
_COORDINATOR_ENTRY = _ROOT / "custom_components" / "lipro" / "coordinator_entry.py"
_CORE_API_INIT = (
    _ROOT / "custom_components" / "lipro" / "core" / "api" / "__init__.py"
)
_CORE_PROTOCOL_INIT = (
    _ROOT / "custom_components" / "lipro" / "core" / "protocol" / "__init__.py"
)
_COORDINATOR_MODULE = (
    _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "coordinator.py"
)
_SERVICE_EXECUTION = _ROOT / "custom_components" / "lipro" / "services" / "execution.py"
_FORBIDDEN_CORE_API_EXPORTS = {
    "client_auth_recovery",
    "client_transport",
    "request_codec",
    "request_policy",
    "response_safety",
    "transport_core",
    "transport_retry",
    "transport_signing",
    "_COMMAND_PACING_CACHE_MAX_SIZE",
    "_mask_sensitive_data",
    "_normalize_response_code",
}
_FORBIDDEN_PROTOCOL_EXPORTS = {
    "BoundaryDecodeResult",
    "BoundaryDecoderKey",
    "BoundaryDecoderRegistry",
    "build_protocol_boundary_registry",
    "decode_mqtt_config_payload",
    "decode_mqtt_properties_payload",
}


def _read_section(text: str, heading: str, next_heading: str | None = None) -> str:
    start = text.index(heading) + len(heading)
    end = text.index(next_heading, start) if next_heading is not None else len(text)
    return text[start:end]


def _extract_all(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id != "__all__":
            continue
        if not isinstance(node.value, (ast.List, ast.Tuple)):
            continue
        return [
            element.value
            for element in node.value.elts
            if isinstance(element, ast.Constant) and isinstance(element.value, str)
        ]
    message = f"Could not find __all__ in {path.relative_to(_ROOT)}"
    raise AssertionError(message)


def _extract_property_names(path: Path, class_name: str) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        property_names: set[str] = set()
        for child in node.body:
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if any(
                isinstance(decorator, ast.Name) and decorator.id == "property"
                for decorator in child.decorator_list
            ):
                property_names.add(child.name)
        return property_names
    message = f"Could not find class {class_name} in {path.relative_to(_ROOT)}"
    raise AssertionError(message)


def test_public_surface_baseline_keeps_canonical_transitional_and_forbidden_roles_distinct() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")
    canonical = _read_section(
        public_surfaces,
        "## Canonical Public Surfaces",
        "## Transitional Public Surfaces",
    )
    transitional = _read_section(
        public_surfaces,
        "## Transitional Public Surfaces",
        "## Forbidden As Formal Roots",
    )
    forbidden = _read_section(
        public_surfaces,
        "## Forbidden As Formal Roots",
        "## Update Rule",
    )

    assert "`Coordinator` + runtime services/public surface" in canonical
    assert (
        "`EntryLifecycleController`, `ServiceRegistry`, `DiagnosticsSurface`, `SystemHealthSurface`"
        in canonical
    )
    assert "`LiproClient` compat shell" not in canonical
    assert "`LiproClient` compat shell" in transitional
    assert "mixin-based mega client" in forbidden
    assert "direct transport/auth objects exposed to entity/control plane" in forbidden
    assert "MQTT client object as runtime/entity public truth" in forbidden
    assert (
        "`core/protocol/boundary/*` decoder package as runtime/control/domain/entity public surface"
        in forbidden
    )
    assert "tests/meta/test_public_surface_guards.py" in public_surfaces


def test_coordinator_entry_exports_only_runtime_surface_symbol() -> None:
    assert _extract_all(_COORDINATOR_ENTRY) == ["Coordinator"]


def test_core_api_package_keeps_transport_internals_out_of_public_exports() -> None:
    public_symbols = set(_extract_all(_CORE_API_INIT))

    assert "LiproClient" in public_symbols
    assert public_symbols.isdisjoint(_FORBIDDEN_CORE_API_EXPORTS)


def test_protocol_root_keeps_boundary_decoder_exports_internal() -> None:
    public_symbols = set(_extract_all(_CORE_PROTOCOL_INIT))

    assert public_symbols.isdisjoint(_FORBIDDEN_PROTOCOL_EXPORTS)


def test_coordinator_runtime_surface_stays_service_oriented() -> None:
    property_names = _extract_property_names(_COORDINATOR_MODULE, "Coordinator")

    assert "devices" in property_names
    assert property_names.isdisjoint(
        {
            "command_runtime",
            "device_runtime",
            "mqtt_runtime",
            "state_runtime",
            "status_runtime",
            "tuning_runtime",
            "background_task_manager",
            "mqtt_client",
            "biz_id",
        }
    )


def test_service_execution_uses_formal_auth_surface_instead_of_private_backdoor() -> None:
    execution_text = _SERVICE_EXECUTION.read_text(encoding="utf-8")

    assert 'getattr(coordinator, "_async_ensure_authenticated"' not in execution_text
    assert 'getattr(coordinator, "_trigger_reauth"' not in execution_text
    assert "auth_service" in execution_text
