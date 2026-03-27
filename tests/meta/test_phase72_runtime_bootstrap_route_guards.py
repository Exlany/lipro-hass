"""Phase 72 runtime/bootstrap no-growth and current-route truth guards."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import (
    _assert_latest_archived_route_truth,
    _assert_public_docs_hide_internal_route_story,
)
from .governance_current_truth import (
    CURRENT_MILESTONE_HEADER,
    CURRENT_ROUTE,
    CURRENT_ROUTE_PROSE_FORBIDDEN,
    CURRENT_RUNTIME_ROOT_TEST,
)

_ROOT = repo_root(Path(__file__))
_PRODUCTION_ROOT = _ROOT / "custom_components" / "lipro"
_LINE_BUDGETS = {
    "core/coordinator/coordinator.py": 345,
    "core/coordinator/orchestrator.py": 330,
    "control/entry_root_wiring.py": 210,
    "control/entry_lifecycle_controller.py": 210,
    "control/entry_lifecycle_support.py": 250,
    "control/runtime_access.py": 340,
    "runtime_infra.py": 440,
}
_FUNCTION_BUDGETS = {
    ("custom_components/lipro/core/coordinator/coordinator.py", "__init__"): 90,
    (
        "custom_components/lipro/core/coordinator/orchestrator.py",
        "build_bootstrap_artifact",
    ): 70,
    ("custom_components/lipro/control/entry_lifecycle_controller.py", "__init__"): 20,
    (
        "custom_components/lipro/control/entry_lifecycle_controller.py",
        "_async_run_entry_activation",
    ): 40,
    ("custom_components/lipro/control/runtime_access.py", "build_runtime_snapshot"): 25,
    (
        "custom_components/lipro/control/runtime_access.py",
        "build_runtime_diagnostics_projection",
    ): 25,
    ("custom_components/lipro/runtime_infra.py", "async_setup_device_registry_listener"): 50,
    (
        "custom_components/lipro/runtime_infra.py",
        "_schedule_reloads_for_device_update",
    ): 35,
}
_PRODUCTION_IMPORT_LOCALITY = {
    "custom_components.lipro.core.coordinator.orchestrator": {
        "custom_components/lipro/core/coordinator/coordinator.py",
    },
    "custom_components.lipro.control.entry_root_wiring": {
        "custom_components/lipro/__init__.py",
        "custom_components/lipro/control/entry_lifecycle_controller.py",
        "custom_components/lipro/control/entry_lifecycle_support.py",
    },
    "custom_components.lipro.control.entry_lifecycle_support": {
        "custom_components/lipro/control/entry_lifecycle_controller.py",
        "custom_components/lipro/control/entry_root_wiring.py",
    },
    "custom_components.lipro.control.runtime_access_support": {
        "custom_components/lipro/control/runtime_access.py",
    },
}
_ROUTE_TESTS = (
    "tests/meta/governance_followup_route_current_milestones.py",
    "tests/meta/test_governance_bootstrap_smoke.py",
    "tests/meta/test_governance_route_handoff_smoke.py",
    "tests/meta/test_governance_milestone_archives.py",
    "tests/meta/test_version_sync.py",
)
_CURRENT_ROUTE_PROSE_PATHS = (
    ".planning/PROJECT.md",
    ".planning/STATE.md",
    ".planning/baseline/PUBLIC_SURFACES.md",
    ".planning/baseline/AUTHORITY_MATRIX.md",
)
_PROJECT_STALE_ARCHIVE_PROJECTIONS = (
    "latest archived evidence index 已升级为 `.planning/reviews/V1_21_EVIDENCE_INDEX.md`；`v1.20` 现固定为 previous archived baseline",
    "当前治理状态已切换为 `no active milestone route / latest archived baseline = v1.21`，并把 `v1.20` 固定为 previous archived baseline。",
    "latest archived evidence index 已升级为 `.planning/reviews/V1_21_EVIDENCE_INDEX.md`；`.planning/reviews/V1_19_EVIDENCE_INDEX.md` 继续只承担 historical / pull-only 身份。",
)


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



def _import_users(module_name: str) -> set[str]:
    users: set[str] = set()
    for path in _iter_production_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
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



def _function_length(relative_path: str, function_name: str) -> int:
    path = _ROOT / relative_path
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            assert node.end_lineno is not None
            return node.end_lineno - node.lineno + 1
    msg = f"Could not find {function_name} in {relative_path}"
    raise AssertionError(msg)



def test_phase72_runtime_bootstrap_line_budgets_hold() -> None:
    for relative_path, budget in _LINE_BUDGETS.items():
        line_count = len(_resolve_target(relative_path).read_text(encoding="utf-8").splitlines())
        assert line_count <= budget, (
            f"{relative_path} grew beyond Phase 72 budget: {line_count} > {budget}"
        )



def test_phase72_runtime_bootstrap_function_budgets_hold() -> None:
    for (relative_path, function_name), budget in _FUNCTION_BUDGETS.items():
        line_count = _function_length(relative_path, function_name)
        assert line_count <= budget, (
            f"{relative_path}:{function_name} grew beyond Phase 72 budget: {line_count} > {budget}"
        )



def test_phase72_runtime_bootstrap_internal_modules_keep_local_importers() -> None:
    for module_name, allowed_users in _PRODUCTION_IMPORT_LOCALITY.items():
        assert _import_users(module_name) == allowed_users



def test_phase72_route_tests_use_shared_current_truth_helper() -> None:
    for relative_path in _ROUTE_TESTS:
        text = (_ROOT / relative_path).read_text(encoding="utf-8")
        assert "governance_current_truth" in text



def test_phase72_current_route_truth_replaces_stale_route_story() -> None:
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    docs_text = (_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    _assert_latest_archived_route_truth(project_text, roadmap_text, state_text)
    assert CURRENT_ROUTE in project_text
    _assert_public_docs_hide_internal_route_story(docs_text)
    assert CURRENT_MILESTONE_HEADER in requirements_text

    for relative_path in _CURRENT_ROUTE_PROSE_PATHS:
        text = (_ROOT / relative_path).read_text(encoding="utf-8")
        for forbidden in CURRENT_ROUTE_PROSE_FORBIDDEN:
            assert forbidden not in text, relative_path

    for stale_projection in _PROJECT_STALE_ARCHIVE_PROJECTIONS:
        assert stale_projection not in project_text



def test_phase72_developer_architecture_points_to_real_runtime_root_tests() -> None:
    docs_text = (_ROOT / "docs" / "developer_architecture.md").read_text(
        encoding="utf-8"
    )

    assert CURRENT_RUNTIME_ROOT_TEST in docs_text
    assert "tests/test_coordinator_public.py" not in docs_text
