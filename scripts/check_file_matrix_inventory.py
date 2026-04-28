"""Inventory helpers for file-governance tooling."""

from __future__ import annotations

from pathlib import Path

EXCLUDED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
}


def repo_root(start: Path | None = None) -> Path:
    """Locate the repository root by walking upward to ``pyproject.toml``."""
    candidate = (start or Path(__file__)).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for parent in (candidate, *candidate.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    msg = "Could not locate repository root"
    raise FileNotFoundError(msg)


def iter_python_files(root: Path) -> list[str]:
    """Return the sorted Python file inventory for governance checks."""
    files: list[str] = []
    for path in root.rglob("*.py"):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIR_NAMES for part in relative.parts):
            continue
        files.append(relative.as_posix())
    return sorted(files)
