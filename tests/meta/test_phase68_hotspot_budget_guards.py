"""Phase 68 hotspot budget guards for review-fed hotspot and docs closeout."""

from __future__ import annotations

import ast
from pathlib import Path

from scripts.check_file_matrix import repo_root

_ROOT = repo_root(Path(__file__))
_PRODUCTION_ROOT = _ROOT / "custom_components" / "lipro"

_LINE_BUDGETS = {
    "core/telemetry/models.py": 230,
    "core/mqtt/message_processor.py": 320,
    "core/mqtt/topics.py": 90,
    "core/anonymous_share/share_client_flows.py": 540,
    "core/api/diagnostics_api_ota.py": 470,
    "runtime_infra.py": 440,
}

_INTERNAL_SUPPORT_IMPORTS = {
    "custom_components.lipro.core.telemetry.outcomes": {
        "custom_components/lipro/core/telemetry/models.py",
    },
    "custom_components.lipro.core.telemetry.json_payloads": {
        "custom_components/lipro/core/telemetry/models.py",
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


def test_phase68_hotspot_line_budgets_hold() -> None:
    for relative_path, budget in _LINE_BUDGETS.items():
        line_count = len(_resolve_target(relative_path).read_text(encoding="utf-8").splitlines())
        assert line_count <= budget, (
            f"{relative_path} grew beyond Phase 68 budget: {line_count} > {budget}"
        )


def test_phase68_telemetry_support_modules_stay_local_to_models() -> None:
    for module_name, allowed_users in _INTERNAL_SUPPORT_IMPORTS.items():
        assert _import_users(module_name) == allowed_users


def test_phase68_mqtt_topic_helper_stays_boundary_backed() -> None:
    topics_text = (_PRODUCTION_ROOT / "core" / "mqtt" / "topics.py").read_text(
        encoding="utf-8"
    )
    message_processor_text = (
        _PRODUCTION_ROOT / "core" / "mqtt" / "message_processor.py"
    ).read_text(encoding="utf-8")

    assert 'import_module("custom_components.lipro.core.protocol.boundary")' in topics_text
    assert "decode_mqtt_topic_payload(" in topics_text
    assert 'topic.split("/")' not in topics_text
    assert "decode_mqtt_topic_payload(" in message_processor_text
