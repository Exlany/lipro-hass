"""Phase 139 mega-facade second-pass slimming guards."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot

_ROOT = repo_root(Path(__file__))
_PRODUCTION_ROOT = _ROOT / "custom_components" / "lipro"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_TESTING = _ROOT / ".planning" / "codebase" / "TESTING.md"
_VERIFICATION = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
_REST_FACADE = _PRODUCTION_ROOT / "core" / "api" / "rest_facade.py"
_REST_FACADE_INTERNAL = _PRODUCTION_ROOT / "core" / "api" / "rest_facade_internal_methods.py"
_REST_FACADE_ENDPOINT_METHODS = (
    _PRODUCTION_ROOT / "core" / "api" / "rest_facade_endpoint_methods.py"
)
_ENDPOINT_SURFACE = _PRODUCTION_ROOT / "core" / "api" / "endpoint_surface.py"
_REST_PORT = _PRODUCTION_ROOT / "core" / "protocol" / "rest_port.py"
_REST_PORT_BINDINGS = _PRODUCTION_ROOT / "core" / "protocol" / "rest_port_bindings.py"

_LINE_BUDGETS = {
    "custom_components/lipro/core/api/rest_facade.py": 300,
    "custom_components/lipro/core/api/endpoint_surface.py": 350,
    "custom_components/lipro/core/protocol/rest_port.py": 230,
}

_PRODUCTION_IMPORT_LOCALITY = {
    "custom_components.lipro.core.api.rest_facade_internal_methods": {
        "custom_components/lipro/core/api/rest_facade.py",
    },
    "custom_components.lipro.core.protocol.rest_port_bindings": {
        "custom_components/lipro/core/protocol/rest_port.py",
    },
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
        tree = ast.parse(_read(path), filename=path.as_posix())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if any(
                    alias.name == module_name or alias.name.startswith(f"{module_name}.")
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


def test_phase139_line_budgets_hold() -> None:
    for relative_path, budget in _LINE_BUDGETS.items():
        line_count = len((_ROOT / relative_path).read_text(encoding="utf-8").splitlines())
        assert line_count <= budget, (
            f"{relative_path} grew beyond Phase 139 budget: {line_count} > {budget}"
        )


def test_phase139_internal_modules_keep_local_importers() -> None:
    for module_name, allowed_users in _PRODUCTION_IMPORT_LOCALITY.items():
        assert _import_users(module_name) == allowed_users


def test_phase139_rest_formal_homes_keep_second_pass_story() -> None:
    rest_facade_text = _read(_REST_FACADE)
    endpoint_methods_text = _read(_REST_FACADE_ENDPOINT_METHODS)
    endpoint_surface_text = _read(_ENDPOINT_SURFACE)
    rest_port_text = _read(_REST_PORT)

    assert "rest_facade_internal_methods import" in rest_facade_text
    assert "_request_smart_home_mapping = _request_smart_home_mapping_impl" in rest_facade_text
    assert "group_id: str = """ in endpoint_methods_text
    assert "group_id=group_id" in endpoint_methods_text
    assert "group_id: str = """ in endpoint_surface_text
    assert "group_id=group_id" in endpoint_surface_text
    assert "from .rest_port_bindings import (" in rest_port_text
    assert "class ProtocolRestPortFamily:" in rest_port_text


def test_phase139_ledgers_register_guard_chain() -> None:
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION)
    file_matrix_text = _read(_FILE_MATRIX)

    assert_testing_inventory_snapshot(testing_text)
    for text in (testing_text, verification_text, file_matrix_text):
        assert "Phase 139" in text
        assert "tests/meta/test_phase139_mega_facade_second_pass_guards.py" in text

    for token in (
        "custom_components/lipro/core/api/rest_facade_internal_methods.py",
        "custom_components/lipro/core/protocol/rest_port_bindings.py",
    ):
        assert token in file_matrix_text
