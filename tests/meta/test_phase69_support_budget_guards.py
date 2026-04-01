"""Phase 69 residual locality and no-growth guards."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_PRODUCTION_ROOT = _ROOT / "custom_components" / "lipro"

_LINE_BUDGETS = {
    "control/runtime_access_support.py": 480,
    "runtime_infra.py": 220,
    "runtime_infra_device_registry.py": 330,
    "services/schedule.py": 350,
    "core/api/client.py": 15,
    "core/api/endpoint_surface.py": 350,
    "core/mqtt/payload.py": 160,
}

_PRODUCTION_IMPORT_LOCALITY = {
    "custom_components.lipro.control.runtime_access_support": {
        "custom_components/lipro/control/runtime_access.py",
    },
    "custom_components.lipro.runtime_infra": {
        "custom_components/lipro/__init__.py",
    },
    "custom_components.lipro.runtime_infra_device_registry": {
        "custom_components/lipro/runtime_infra.py",
    },
    "custom_components.lipro.services.schedule": {
        "custom_components/lipro/control/service_router_schedule_handlers.py",
    },
    "custom_components.lipro.core.api.client": {
        "custom_components/lipro/core/api/__init__.py",
        "custom_components/lipro/core/protocol/facade.py",
    },
    "custom_components.lipro.core.api.endpoint_surface": {
        "custom_components/lipro/core/api/rest_facade.py",
    },
    "custom_components.lipro.core.mqtt.payload": {
        "custom_components/lipro/core/mqtt/message_processor.py",
        "custom_components/lipro/core/mqtt/transport_runtime.py",
    },
}


def _resolve_target(relative_path: str) -> Path:
    return _PRODUCTION_ROOT / relative_path


def _relative_repo_path(path: Path) -> str:
    return path.relative_to(_ROOT).as_posix()


def _iter_production_sources() -> list[Path]:
    return sorted((_ROOT / "custom_components").rglob("*.py"))


def _module_name_for_path(path: Path) -> str:
    parts = list(path.relative_to(_ROOT).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _resolve_imported_module(path: Path, node: ast.ImportFrom) -> str | None:
    if node.level == 0:
        return node.module

    module_parts = _module_name_for_path(path).split(".")
    package_parts = module_parts if path.name == "__init__.py" else module_parts[:-1]
    anchor = package_parts[: len(package_parts) - (node.level - 1)]
    if node.module is not None:
        anchor.append(node.module)
    return ".".join(anchor) if anchor else None


def _imported_module_names(path: Path, node: ast.ImportFrom) -> set[str]:
    base = _resolve_imported_module(path, node)
    if base is None:
        return set()
    if node.module is not None:
        return {base}
    return {f"{base}.{alias.name}" for alias in node.names}


def _import_users(module_name: str) -> set[str]:
    users: set[str] = set()
    for path in _iter_production_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if any(
                    alias.name == module_name
                    or alias.name.startswith(f"{module_name}.")
                    for alias in node.names
                ):
                    users.add(_relative_repo_path(path))
            elif isinstance(node, ast.ImportFrom):
                imported_modules = _imported_module_names(path, node)
                if any(
                    imported_module == module_name
                    or imported_module.startswith(f"{module_name}.")
                    for imported_module in imported_modules
                ):
                    users.add(_relative_repo_path(path))
    return users


def test_phase69_residual_line_budgets_hold() -> None:
    for relative_path, budget in _LINE_BUDGETS.items():
        line_count = len(
            _resolve_target(relative_path).read_text(encoding="utf-8").splitlines()
        )
        assert line_count <= budget, (
            f"{relative_path} grew beyond Phase 69 budget: {line_count} > {budget}"
        )


def test_phase69_residual_modules_keep_local_importers() -> None:
    for module_name, allowed_users in _PRODUCTION_IMPORT_LOCALITY.items():
        assert _import_users(module_name) == allowed_users


def test_phase69_runtime_access_support_stays_formal_home_locality_only() -> None:
    runtime_access_text = (
        _PRODUCTION_ROOT / "control" / "runtime_access.py"
    ).read_text(encoding="utf-8")
    telemetry_surface_text = (
        _PRODUCTION_ROOT / "control" / "telemetry_surface.py"
    ).read_text(encoding="utf-8")
    diagnostics_surface_text = (
        _PRODUCTION_ROOT / "control" / "diagnostics_surface.py"
    ).read_text(encoding="utf-8")
    system_health_surface_text = (
        _PRODUCTION_ROOT / "control" / "system_health_surface.py"
    ).read_text(encoding="utf-8")

    assert "from . import runtime_access_support as _support" in runtime_access_text
    assert "runtime_access_support" not in telemetry_surface_text
    assert "runtime_access_support" not in diagnostics_surface_text
    assert "runtime_access_support" not in system_health_surface_text
