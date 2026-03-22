"""Markdown render and parse helpers for `FILE_MATRIX.md`."""

from __future__ import annotations

from collections.abc import Iterable
import re

from scripts.check_file_matrix_registry import classify_path

FILE_MATRIX_HEADER_PATTERN = re.compile(r"\*\*Python files total:\*\*\s+(\d+)")

FILE_MATRIX_ROW_PATTERN = re.compile(r"^\| `([^`]+\.py)` \|", re.MULTILINE)



def generate_file_matrix_markdown(files: Iterable[str]) -> str:
    """Render the current Python inventory into ``FILE_MATRIX.md`` markdown."""
    rows = [classify_path(path) for path in files]
    lines = [
        "# File Matrix",
        "",
        f"**Python files total:** {len(rows)}",
        "**Status:** File-level governance authority",
        "**Rule:** workspace inventory excluding caches / virtual env / tooling artifacts",
        "",
        "## File-Level Governance Matrix",
        "",
        "| Path | Area | Owner phase | Fate | Residual / delete gate |",
        "|------|------|-------------|------|-------------------------|",
    ]
    for row in rows:
        lines.append(
            f"| `{row.path}` | {row.area} | {row.owner_phase} | {row.fate} | {row.residual} |"
        )
    return "\n".join(lines) + "\n"



def parse_file_matrix_paths(text: str) -> list[str]:
    """Extract Python file paths from the file-matrix markdown table."""
    return FILE_MATRIX_ROW_PATTERN.findall(text)



def extract_reported_total(text: str) -> int:
    """Extract the declared Python file count from file-matrix markdown."""
    match = FILE_MATRIX_HEADER_PATTERN.search(text)
    if match is None:
        msg = "FILE_MATRIX missing '**Python files total:** <n>' header"
        raise ValueError(msg)
    return int(match.group(1))
