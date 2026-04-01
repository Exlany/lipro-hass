"""Phase 113 hotspot assurance and helper-locality historical guards."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot

_ROOT = repo_root(Path(__file__))
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_KILL_LIST = _ROOT / ".planning" / "reviews" / "KILL_LIST.md"
_RESIDUAL_LEDGER = _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
_TESTING = _ROOT / ".planning" / "codebase" / "TESTING.md"
_VERIFICATION_MATRIX = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"

_LINE_BUDGETS = {
    "custom_components/lipro/core/api/status_fallback_support.py": 340,
    "custom_components/lipro/core/api/rest_facade.py": 360,
    "custom_components/lipro/core/anonymous_share/manager.py": 359,
    "custom_components/lipro/core/protocol/boundary/rest_decoder.py": 210,
    "custom_components/lipro/entities/firmware_update.py": 418,
    "custom_components/lipro/core/protocol/boundary/rest_decoder_support.py": 180,
    "custom_components/lipro/core/command/result_policy.py": 417,
    "custom_components/lipro/core/command/dispatch.py": 412,
    "custom_components/lipro/core/auth/manager.py": 407,
    "custom_components/lipro/core/anonymous_share/share_client_submit.py": 170,
    "custom_components/lipro/core/command/result.py": 398,
}

_INTERNAL_IMPORT_LOCALITY = {
    "custom_components.lipro.core.api.status_fallback_split_executor": {
        "custom_components/lipro/core/api/status_fallback_support.py",
    },
    "custom_components.lipro.core.api.status_fallback_summary_logging": {
        "custom_components/lipro/core/api/status_fallback_split_executor.py",
    },
    "custom_components.lipro.core.anonymous_share.share_client_submit_attempts": {
        "custom_components/lipro/core/anonymous_share/share_client_submit.py",
    },
    "custom_components.lipro.core.anonymous_share.share_client_submit_outcomes": {
        "custom_components/lipro/core/anonymous_share/share_client_submit.py",
        "custom_components/lipro/core/anonymous_share/share_client_submit_attempts.py",
    },
    "custom_components.lipro.core.command.result_support": {
        "custom_components/lipro/core/command/result.py",
    },
    "custom_components.lipro.core.protocol.boundary.rest_decoder_family": {
        "custom_components/lipro/core/protocol/boundary/rest_decoder.py",
    },
    "custom_components.lipro.core.protocol.boundary.rest_decoder_registry": {
        "custom_components/lipro/core/protocol/boundary/rest_decoder.py",
        "custom_components/lipro/core/protocol/boundary/rest_decoder_family.py",
    },
    "custom_components.lipro.core.protocol.boundary.rest_decoder_utility": {
        "custom_components/lipro/core/protocol/boundary/rest_decoder.py",
        "custom_components/lipro/core/protocol/boundary/rest_decoder_family.py",
        "custom_components/lipro/core/protocol/boundary/rest_decoder_support.py",
    },
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _iter_python_sources() -> list[Path]:
    return sorted(path for path in _ROOT.rglob("*.py") if "/.venv/" not in path.as_posix())


def _relative_repo_path(path: Path) -> str:
    return path.relative_to(_ROOT).as_posix()


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


def _import_users(module_name: str) -> set[str]:
    users: set[str] = set()
    for path in _iter_python_sources():
        tree = ast.parse(_read(path), filename=path.as_posix())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if any(
                    alias.name == module_name or alias.name.startswith(f"{module_name}.")
                    for alias in node.names
                ):
                    users.add(_relative_repo_path(path))
            elif isinstance(node, ast.ImportFrom):
                imported_module = _resolve_imported_module(path, node)
                if imported_module is None:
                    continue
                if imported_module == module_name or imported_module.startswith(
                    f"{module_name}."
                ):
                    users.add(_relative_repo_path(path))
    return users


def test_phase113_hotspot_line_budgets_hold() -> None:
    for relative_path, budget in _LINE_BUDGETS.items():
        line_count = len((_ROOT / relative_path).read_text(encoding="utf-8").splitlines())
        assert line_count <= budget, (
            f"{relative_path} grew beyond Phase 113 budget: {line_count} > {budget}"
        )


def test_phase113_helper_modules_keep_local_importers() -> None:
    for module_name, allowed_users in _INTERNAL_IMPORT_LOCALITY.items():
        assert _import_users(module_name) == allowed_users


def test_phase113_ledgers_record_hotspot_freeze_and_guard_chain() -> None:
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)
    file_matrix_text = _read(_FILE_MATRIX)
    residual_text = _read(_RESIDUAL_LEDGER)
    kill_text = _read(_KILL_LIST)

    assert_testing_inventory_snapshot(testing_text)
    for text in (testing_text, verification_text, file_matrix_text, residual_text, kill_text):
        assert "Phase 113" in text

    for text in (testing_text, verification_text, file_matrix_text):
        assert "tests/meta/test_phase113_hotspot_assurance_guards.py" in text

    for token in (
        "status_fallback_support.py",
        "rest_facade.py",
        "anonymous_share/manager.py",
        "rest_decoder.py",
        "firmware_update.py",
        "result_policy.py",
        "dispatch.py",
        "auth/manager.py",
    ):
        assert token in residual_text
        assert token in kill_text

