"""Phase 89 tooling-kernel decoupling regression guards."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_ARCHITECTURE_CHECKER = _ROOT / 'scripts' / 'check_architecture_policy.py'
_FILE_MATRIX_CHECKER = _ROOT / 'scripts' / 'check_file_matrix.py'
_SCRIPT_ARCH = _ROOT / 'scripts' / 'lib' / 'architecture_policy.py'
_SCRIPT_AST = _ROOT / 'scripts' / 'lib' / 'ast_guard_utils.py'
_TEST_ARCH = _ROOT / 'tests' / 'helpers' / 'architecture_policy.py'
_TEST_AST = _ROOT / 'tests' / 'helpers' / 'ast_guard_utils.py'
_ROOT_ADAPTER = _ROOT / 'custom_components' / 'lipro' / '__init__.py'
_CONTROL_SERVICE_REGISTRY = _ROOT / 'custom_components' / 'lipro' / 'control' / 'service_registry.py'
_EXPECTED_FILE_MATRIX_MODULES = {
    'check_file_matrix_inventory',
    'check_file_matrix_markdown',
    'check_file_matrix_registry',
    'check_file_matrix_validation',
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _load_ast(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding='utf-8'))


def _import_from_modules(tree: ast.AST) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module)
    return modules


def _string_constants(tree: ast.AST) -> set[str]:
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


def _has_sys_path_insert(text: str) -> bool:
    return 'sys.path.insert' in text


def _has_importlib_import_module_call(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            if func.value.id == 'importlib' and func.attr == 'import_module':
                return True
    return False


def test_phase89_governance_cli_roots_consume_script_owned_helpers_only() -> None:
    architecture_checker_text = _read_text(_ARCHITECTURE_CHECKER)
    file_matrix_checker_text = _read_text(_FILE_MATRIX_CHECKER)
    architecture_checker_tree = _load_ast(_ARCHITECTURE_CHECKER)
    file_matrix_checker_tree = _load_ast(_FILE_MATRIX_CHECKER)

    assert 'tests.helpers.architecture_policy' not in architecture_checker_text
    assert 'tests.helpers.ast_guard_utils' not in architecture_checker_text
    assert not _has_sys_path_insert(architecture_checker_text)
    assert {'scripts.lib.architecture_policy', 'scripts.lib.ast_guard_utils'} <= _import_from_modules(
        architecture_checker_tree
    )
    assert {'lib.architecture_policy', 'lib.ast_guard_utils'} <= _import_from_modules(
        architecture_checker_tree
    )

    assert 'tests.helpers' not in file_matrix_checker_text
    assert not _has_sys_path_insert(file_matrix_checker_text)
    assert _has_importlib_import_module_call(file_matrix_checker_tree)
    assert _string_constants(file_matrix_checker_tree) >= _EXPECTED_FILE_MATRIX_MODULES
    imported_modules = _import_from_modules(file_matrix_checker_tree)
    assert 'scripts.check_file_matrix_inventory' not in imported_modules
    assert 'scripts.check_file_matrix_markdown' not in imported_modules
    assert 'scripts.check_file_matrix_registry' not in imported_modules
    assert 'scripts.check_file_matrix_validation' not in imported_modules
    assert 'check_file_matrix_inventory' not in imported_modules
    assert 'check_file_matrix_markdown' not in imported_modules
    assert 'check_file_matrix_registry' not in imported_modules
    assert 'check_file_matrix_validation' not in imported_modules


def test_phase89_tests_helpers_are_thin_re_exports_only() -> None:
    architecture_helper_text = _read_text(_TEST_ARCH)
    ast_helper_text = _read_text(_TEST_AST)

    assert 'from scripts.lib.architecture_policy import' in architecture_helper_text
    assert 'from scripts.lib.ast_guard_utils import' in ast_helper_text
    assert '@dataclass' not in architecture_helper_text
    assert 'def policy_root' not in architecture_helper_text
    assert 'def load_structural_rules' not in architecture_helper_text
    assert 'def iter_import_modules' not in ast_helper_text
    assert 'ast.parse' not in ast_helper_text


def test_phase89_script_lib_is_the_real_helper_home() -> None:
    architecture_text = _read_text(_SCRIPT_ARCH)
    ast_text = _read_text(_SCRIPT_AST)

    assert '@dataclass(frozen=True, slots=True)' in architecture_text
    assert 'def policy_root' in architecture_text
    assert 'def load_structural_rules' in architecture_text
    assert 'def iter_import_modules' in ast_text
    assert 'def extract_all' in ast_text


def test_phase89_root_adapter_builds_service_registry_via_control_surface() -> None:
    root_adapter_text = _read_text(_ROOT_ADAPTER)
    control_registry_text = _read_text(_CONTROL_SERVICE_REGISTRY)

    assert 'from .services.registry import' not in root_adapter_text
    assert 'build_service_registry as _build_service_registry_impl' in root_adapter_text
    assert '_build_service_registry_impl(' in root_adapter_text
    assert 'def build_default_service_registry' in control_registry_text
    assert 'async_setup_services as _async_setup_services_impl' in control_registry_text
