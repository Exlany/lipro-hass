"""Phase 70 hotspot, archive-freeze, and helper-locality guards."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_PRODUCTION_ROOT = _ROOT / "custom_components" / "lipro"

_LINE_BUDGETS = {
    "control/runtime_access_support.py": 120,
    "core/anonymous_share/share_client_flows.py": 100,
    "core/api/diagnostics_api_ota.py": 410,
    "core/ota/query_support.py": 100,
}

_INTERNAL_IMPORT_LOCALITY = {
    "custom_components.lipro.control.runtime_access_support_members": {
        "custom_components/lipro/control/runtime_access_support_devices.py",
        "custom_components/lipro/control/runtime_access_support_telemetry.py",
        "custom_components/lipro/control/runtime_access_support_views.py",
    },
    "custom_components.lipro.control.runtime_access_support_telemetry": {
        "custom_components/lipro/control/runtime_access_support.py",
        "custom_components/lipro/control/runtime_access_support_views.py",
    },
    "custom_components.lipro.control.runtime_access_support_views": {
        "custom_components/lipro/control/runtime_access_support.py",
        "custom_components/lipro/control/runtime_access_support_devices.py",
    },
    "custom_components.lipro.control.runtime_access_support_devices": {
        "custom_components/lipro/control/runtime_access_support.py",
    },
    "custom_components.lipro.core.anonymous_share.share_client_ports": {
        "custom_components/lipro/core/anonymous_share/share_client_flows.py",
        "custom_components/lipro/core/anonymous_share/share_client_refresh.py",
        "custom_components/lipro/core/anonymous_share/share_client_submit.py",
    },
    "custom_components.lipro.core.anonymous_share.share_client_refresh": {
        "custom_components/lipro/core/anonymous_share/share_client_flows.py",
    },
    "custom_components.lipro.core.anonymous_share.share_client_submit": {
        "custom_components/lipro/core/anonymous_share/share_client_flows.py",
    },
    "custom_components.lipro.core.ota.query_support": {
        "custom_components/lipro/core/api/diagnostics_api_ota.py",
    },
}


def _resolve_target(relative_path: str) -> Path:
    return _PRODUCTION_ROOT / relative_path


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

    module_parts = _module_name_for_path(path).split(".")
    package_parts = module_parts if path.name == "__init__.py" else module_parts[:-1]
    anchor = package_parts[: len(package_parts) - (node.level - 1)]
    if node.module is not None:
        anchor.append(node.module)
    return ".".join(anchor) if anchor else None


def _import_users(module_name: str) -> set[str]:
    users: set[str] = set()
    for path in _iter_python_sources():
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


def test_phase70_hotspot_line_budgets_hold() -> None:
    for relative_path, budget in _LINE_BUDGETS.items():
        line_count = len(_resolve_target(relative_path).read_text(encoding="utf-8").splitlines())
        assert line_count <= budget, (
            f"{relative_path} grew beyond Phase 70 budget: {line_count} > {budget}"
        )


def test_phase70_internal_helper_modules_keep_local_importers() -> None:
    for module_name, allowed_users in _INTERNAL_IMPORT_LOCALITY.items():
        assert _import_users(module_name) == allowed_users


def test_phase70_version_sync_stops_reading_archived_phase_assets() -> None:
    version_sync_text = (_ROOT / "tests" / "meta" / "test_version_sync.py").read_text(
        encoding="utf-8"
    )
    assert "_PHASE_15_PRD" not in version_sync_text
    assert "_PHASE_15_CONTEXT" not in version_sync_text
    assert '_V1_17_EVIDENCE_INDEX.read_text' not in version_sync_text


def test_phase70_archive_tokens_live_in_archive_family_not_version_sync() -> None:
    version_sync_text = (_ROOT / "tests" / "meta" / "test_version_sync.py").read_text(
        encoding="utf-8"
    )
    milestone_archive_family_paths = (
        _ROOT / "tests" / "meta" / "test_governance_milestone_archives.py",
        _ROOT / "tests" / "meta" / "governance_milestone_archives_assets.py",
        _ROOT / "tests" / "meta" / "governance_milestone_archives_truth.py",
        _ROOT / "tests" / "meta" / "governance_milestone_archives_ordering.py",
    )
    milestone_archive_family_text = "\n".join(
        path.read_text(encoding="utf-8") for path in milestone_archive_family_paths
    )

    assert "69-SUMMARY.md" not in version_sync_text
    assert "69-VERIFICATION.md" not in version_sync_text
    assert "69-SUMMARY.md" in milestone_archive_family_text
    assert "69-VERIFICATION.md" in milestone_archive_family_text
