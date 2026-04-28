"""Thin compatibility re-export for AST guard helpers."""

from __future__ import annotations

from scripts.lib.ast_guard_utils import (
    extract_all,
    extract_property_names,
    extract_top_level_bindings,
    find_forbidden_imports,
    iter_import_modules,
)

__all__ = [
    "extract_all",
    "extract_property_names",
    "extract_top_level_bindings",
    "find_forbidden_imports",
    "iter_import_modules",
]
