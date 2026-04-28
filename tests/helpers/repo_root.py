"""Repository root detection helpers for path-based tests."""

from __future__ import annotations

from pathlib import Path


def repo_root(start: Path | None = None) -> Path:
    """Return the repository root directory containing `pyproject.toml`.

    Args:
        start: Optional starting path (file or directory). Defaults to this file.
    """
    candidate = (start or Path(__file__)).resolve()
    if candidate.is_file():
        candidate = candidate.parent

    for parent in (candidate, *candidate.parents):
        if (parent / "pyproject.toml").is_file():
            return parent

    msg = "Could not locate repository root (pyproject.toml)"
    raise FileNotFoundError(msg)
