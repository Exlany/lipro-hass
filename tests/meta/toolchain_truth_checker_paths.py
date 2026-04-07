"""Checker-path truth and local development smoke guards."""

from __future__ import annotations

import ast
import importlib
import os
from pathlib import Path
import shutil
import stat
import subprocess

from tests.helpers.repo_root import repo_root

from .governance_current_truth import CURRENT_RUNTIME_ROOT_TEST

_ROOT = repo_root(Path(__file__))
_RUNBOOK = _ROOT / 'docs' / 'MAINTAINER_RELEASE_RUNBOOK.md'
_ROUTE_HANDOFF_SMOKE = _ROOT / 'tests' / 'meta' / 'test_governance_route_handoff_smoke.py'
_DEVELOP_SCRIPT = _ROOT / 'scripts' / 'develop'
_CHECKER_SCRIPT = _ROOT / 'scripts' / 'check_file_matrix.py'
_CONFTEXT = _ROOT / 'tests' / 'conftest.py'
_EXPECTED_CHECKER_MODULES = {
    'check_file_matrix_inventory',
    'check_file_matrix_markdown',
    'check_file_matrix_registry',
    'check_file_matrix_validation',
}


def _load_ast(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding='utf-8'))


def _collect_string_constants(tree: ast.AST) -> set[str]:
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


def _has_importlib_import_module_call(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            if func.value.id == 'importlib' and func.attr == 'import_module':
                return True
    return False


def test_verification_matrix_and_checker_guard_active_path_truth() -> None:
    verification_text = (_ROOT / '.planning' / 'baseline' / 'VERIFICATION_MATRIX.md').read_text(
        encoding='utf-8'
    )
    docs_text = (_ROOT / 'docs' / 'developer_architecture.md').read_text(encoding='utf-8')
    checker_tree = _load_ast(_CHECKER_SCRIPT)
    checker_text = _CHECKER_SCRIPT.read_text(encoding='utf-8')
    checker_module = importlib.import_module('scripts.check_file_matrix')
    conftest_text = _CONFTEXT.read_text(encoding='utf-8')
    runbook_text = _RUNBOOK.read_text(encoding='utf-8')
    route_smoke_text = _ROUTE_HANDOFF_SMOKE.read_text(encoding='utf-8')

    assert 'tests/core/anonymous_share/test_manager_submission.py' in verification_text
    assert 'tests/core/test_coordinator_entry.py' in verification_text
    assert 'tests/core/test_diagnostics*.py' in verification_text
    assert 'tests/core/test_anonymous_share.py' not in verification_text
    assert 'tests/test_coordinator_public.py' not in verification_text
    assert 'tests/test_coordinator_runtime.py' not in verification_text
    assert CURRENT_RUNTIME_ROOT_TEST in docs_text
    assert 'docs/architecture_archive.md' in docs_text
    assert 'tests/test_coordinator_public.py' not in docs_text
    assert 'nested worktree' in docs_text
    assert 'nested worktree' in runbook_text
    assert '--cwd' in runbook_text
    assert 'symlink_to' in route_smoke_text
    assert '--cwd=' in route_smoke_text
    assert 'VERIFICATION_MATRIX_PATH' in checker_text
    assert 'validate_verification_matrix_paths' in checker_text
    assert 'TYPE_CHECKING' not in checker_text
    assert 'sys.path.insert' not in checker_text
    assert _has_importlib_import_module_call(checker_tree)
    assert _collect_string_constants(checker_tree) >= _EXPECTED_CHECKER_MODULES
    assert checker_module.iter_python_files.__module__ in {
        'check_file_matrix_inventory',
        'scripts.check_file_matrix_inventory',
    }
    assert checker_module.classify_path.__module__ in {
        'check_file_matrix_registry',
        'scripts.check_file_matrix_registry',
    }
    assert 'Phase 60 Tooling Truth Decomposition Contract' in verification_text
    assert 'scripts/check_file_matrix_inventory.py' in verification_text
    assert 'tests/meta/toolchain_truth_python_stack.py' in verification_text
    assert 'uv add --dev pytest-homeassistant-custom-component' in conftest_text
    assert 'pip install pytest-homeassistant-custom-component' not in conftest_text


def test_develop_script_smoke_mode_preserves_other_integrations(
    tmp_path: Path,
) -> None:
    """The local development entrypoint should only refresh Lipro's integration."""
    fake_repo = tmp_path / 'repo'
    scripts_dir = fake_repo / 'scripts'
    source_lipro = fake_repo / 'custom_components' / 'lipro'
    keep_component = fake_repo / 'config' / 'custom_components' / 'keep_me'
    fake_bin = tmp_path / 'bin'
    fake_uv = fake_bin / 'uv'
    copied_script = scripts_dir / 'develop'

    scripts_dir.mkdir(parents=True)
    source_lipro.mkdir(parents=True)
    keep_component.mkdir(parents=True)
    fake_bin.mkdir(parents=True)
    (fake_repo / '.venv').mkdir()

    copied_script.write_text(
        _DEVELOP_SCRIPT.read_text(encoding='utf-8'), encoding='utf-8'
    )
    copied_script.chmod(copied_script.stat().st_mode | stat.S_IXUSR)
    (source_lipro / 'manifest.json').write_text(
        '{"domain": "lipro"}',
        encoding='utf-8',
    )
    (keep_component / 'sentinel.txt').write_text('keep', encoding='utf-8')
    fake_uv.write_text('#!/usr/bin/env bash\nexit 0\n', encoding='utf-8')
    fake_uv.chmod(fake_uv.stat().st_mode | stat.S_IXUSR)

    env = os.environ.copy()
    env['PATH'] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    env['LIPRO_DEVELOP_SMOKE_ONLY'] = '1'

    bash_executable = shutil.which('bash')
    assert bash_executable is not None

    result = subprocess.run(  # noqa: S603
        [bash_executable, str(copied_script)],
        cwd=fake_repo,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert (
        fake_repo / 'config' / 'custom_components' / 'keep_me' / 'sentinel.txt'
    ).read_text(encoding='utf-8') == 'keep'
    assert (
        fake_repo / 'config' / 'custom_components' / 'lipro' / 'manifest.json'
    ).exists()
    assert 'Preserved other custom integrations' in result.stdout
    assert 'Smoke-only mode' in result.stdout
    assert 'rm -rf config/custom_components' not in _DEVELOP_SCRIPT.read_text(
        encoding='utf-8'
    )
