"""Governance guards for file-matrix coverage and authority hygiene."""

from __future__ import annotations

from pathlib import Path

from scripts.check_file_matrix import (
    extract_reported_total,
    iter_python_files,
    parse_file_matrix_paths,
    repo_root,
    run_checks,
)

_ROOT = repo_root(Path(__file__))
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"


def test_file_matrix_covers_workspace_python_inventory() -> None:
    inventory = iter_python_files(_ROOT)
    matrix_text = _FILE_MATRIX.read_text(encoding="utf-8")

    assert extract_reported_total(matrix_text) == len(inventory)
    assert parse_file_matrix_paths(matrix_text) == inventory


def test_governance_checker_reports_no_drift() -> None:
    assert run_checks(_ROOT) == []
