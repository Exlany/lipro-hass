"""Seed dependency guards for baseline architecture boundaries."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_DEPENDENCY_MATRIX = _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"

_ENTITY_PLATFORM_SEED_PATHS = [
    _ROOT / "custom_components" / "lipro" / "binary_sensor.py",
    _ROOT / "custom_components" / "lipro" / "climate.py",
    _ROOT / "custom_components" / "lipro" / "cover.py",
    _ROOT / "custom_components" / "lipro" / "fan.py",
    _ROOT / "custom_components" / "lipro" / "light.py",
    _ROOT / "custom_components" / "lipro" / "select.py",
    _ROOT / "custom_components" / "lipro" / "sensor.py",
    _ROOT / "custom_components" / "lipro" / "switch.py",
    _ROOT / "custom_components" / "lipro" / "update.py",
    _ROOT / "custom_components" / "lipro" / "helpers" / "platform.py",
]
_ENTITY_SUPPORT_SEED_PATHS = sorted(
    (_ROOT / "custom_components" / "lipro" / "entities").glob("*.py")
)
_CONTROL_SURFACE_SEED_PATHS = [
    _ROOT / "custom_components" / "lipro" / "runtime_infra.py",
    _ROOT / "custom_components" / "lipro" / "diagnostics.py",
    _ROOT / "custom_components" / "lipro" / "system_health.py",
    _ROOT / "custom_components" / "lipro" / "services" / "registry.py",
    _ROOT / "custom_components" / "lipro" / "services" / "registrations.py",
    _ROOT / "custom_components" / "lipro" / "control" / "entry_lifecycle_controller.py",
    _ROOT / "custom_components" / "lipro" / "control" / "runtime_access.py",
    _ROOT / "custom_components" / "lipro" / "control" / "service_registry.py",
    _ROOT / "custom_components" / "lipro" / "control" / "service_router.py",
    _ROOT / "custom_components" / "lipro" / "control" / "diagnostics_surface.py",
    _ROOT / "custom_components" / "lipro" / "control" / "system_health_surface.py",
]

_PROTOCOL_INTERNAL_PREFIXES = (
    ".core.api",
    "..core.api",
    "custom_components.lipro.core.api",
    ".core.mqtt",
    "..core.mqtt",
    "custom_components.lipro.core.mqtt",
)
_CONTROL_ONLY_FORBIDDEN_PREFIXES = (
    ".core.coordinator",
    "..core.coordinator",
    "custom_components.lipro.core.coordinator",
)


def _iter_import_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
            continue
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            dotted = f"{'.' * node.level}{module}" if node.level else module
            if dotted:
                modules.add(dotted)

    return sorted(modules)


def _find_forbidden_imports(
    paths: list[Path], forbidden_prefixes: tuple[str, ...]
) -> list[str]:
    violations: list[str] = []
    for path in paths:
        bad_imports = [
            module
            for module in _iter_import_modules(path)
            if any(
                module == prefix or module.startswith(f"{prefix}.")
                for prefix in forbidden_prefixes
            )
        ]
        if bad_imports:
            joined = ", ".join(bad_imports)
            violations.append(f"{path.relative_to(_ROOT)} -> {joined}")
    return violations


def test_dependency_matrix_documents_seed_guard_scope() -> None:
    dependency_matrix = _DEPENDENCY_MATRIX.read_text(encoding="utf-8")

    assert (
        "| Entity / Platform | raw protocol internals, MQTT client, REST transport |"
        in dependency_matrix
    )
    assert (
        "| Control plane | protocol internals, runtime internals bypassing public surface |"
        in dependency_matrix
    )
    assert "tests/meta/test_dependency_guards.py" in dependency_matrix
    assert "core.api`、`core.mqtt` 与 `core.coordinator` internals" in dependency_matrix
    assert "control/" in dependency_matrix


def test_entity_seed_files_do_not_import_protocol_internals_directly() -> None:
    violations = _find_forbidden_imports(
        _ENTITY_PLATFORM_SEED_PATHS + _ENTITY_SUPPORT_SEED_PATHS,
        _PROTOCOL_INTERNAL_PREFIXES,
    )
    assert not violations, "\n".join(violations)


def test_control_surface_seed_files_do_not_bypass_public_runtime_surfaces() -> None:
    violations = _find_forbidden_imports(
        _CONTROL_SURFACE_SEED_PATHS,
        _PROTOCOL_INTERNAL_PREFIXES + _CONTROL_ONLY_FORBIDDEN_PREFIXES,
    )
    assert not violations, "\n".join(violations)
