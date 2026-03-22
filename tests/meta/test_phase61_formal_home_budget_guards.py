"""Phase 61 formal-home hotspot guards for production slimming work."""

from __future__ import annotations

import ast
from pathlib import Path
import re

from scripts.check_file_matrix import repo_root

_ROOT = repo_root(Path(__file__))
_PRODUCTION_ROOT = _ROOT / "custom_components" / "lipro"
_ANY_LINE_RE = re.compile(r"\bAny\b")
_BROAD_CATCH_LINE_RE = re.compile(r"except Exception|with suppress\(Exception\)")

_LINE_BUDGETS = {
    "core/anonymous_share/manager.py": 419,
    "core/anonymous_share/share_client.py": 131,
    "services/diagnostics/helpers.py": 298,
    "services/diagnostics/handlers.py": 163,
    "core/ota/candidate.py": 229,
    "core/ota/candidate_support.py": 249,
    "select.py": 400,
    "select_internal/gear.py": 130,
}

_CLEAN_SUPPORT_TARGETS = {
    "core/ota/candidate.py",
    "core/ota/candidate_support.py",
    "select.py",
    "select_internal/gear.py",
}

_INTERNAL_SUPPORT_IMPORTS = {
    "custom_components.lipro.core.ota.candidate_support": {
        "custom_components/lipro/core/ota/candidate.py",
    },
    "custom_components.lipro.select_internal.gear": {
        "custom_components/lipro/select.py",
    },
}


def _resolve_target(relative_path: str) -> Path:
    return _PRODUCTION_ROOT / relative_path


def _count_matching_lines(path: Path, pattern: re.Pattern[str]) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if pattern.search(line))


def _relative_repo_path(path: Path) -> str:
    return path.relative_to(_ROOT).as_posix()


def _iter_python_sources() -> list[Path]:
    return sorted(path for path in _ROOT.rglob("*.py") if "/.venv/" not in path.as_posix())


def _module_name_for_path(path: Path) -> str:
    parts = list(path.relative_to(_ROOT).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _resolve_imported_module(path: Path, node: ast.ImportFrom) -> str | None:
    if node.level == 0:
        return node.module

    package_parts = _module_name_for_path(path).split(".")[:-1]
    anchor = package_parts[: len(package_parts) - (node.level - 1)]
    if node.module is not None:
        anchor.append(node.module)
    return ".".join(anchor) if anchor else None


def _import_users(module_name: str) -> set[str]:
    users: set[str] = set()
    for path in _iter_python_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"))
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


def test_phase61_formal_home_line_budgets_hold() -> None:
    for relative_path, budget in _LINE_BUDGETS.items():
        line_count = len(_resolve_target(relative_path).read_text(encoding="utf-8").splitlines())
        assert line_count <= budget, (
            f"{relative_path} grew beyond Phase 61 budget: {line_count} > {budget}"
        )


def test_phase61_select_and_ota_support_modules_keep_clean_type_and_exception_surface() -> None:
    for relative_path in sorted(_CLEAN_SUPPORT_TARGETS):
        path = _resolve_target(relative_path)
        text = path.read_text(encoding="utf-8")
        assert _count_matching_lines(path, _ANY_LINE_RE) == 0
        assert _count_matching_lines(path, _BROAD_CATCH_LINE_RE) == 0
        assert "type: ignore" not in text


def test_phase61_internal_support_modules_stay_local_to_formal_homes() -> None:
    for module_name, allowed_users in _INTERNAL_SUPPORT_IMPORTS.items():
        assert _import_users(module_name) == allowed_users
