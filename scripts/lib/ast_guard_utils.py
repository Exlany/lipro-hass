"""Shared AST helpers for architecture guard checks."""

from __future__ import annotations

import ast
from pathlib import Path


def iter_import_modules(path: Path) -> list[str]:
    """Return imported module prefixes from one Python file."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
            continue
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            dotted = f"{'.' * node.level}{module}" if node.level else module
            if dotted:
                modules.add(dotted)

    return sorted(modules)


def find_forbidden_imports(
    paths: list[Path],
    forbidden_prefixes: tuple[str, ...],
    *,
    root: Path,
) -> list[str]:
    """Return formatted import violations for one path set."""
    violations: list[str] = []
    for path in paths:
        bad_imports = [
            module
            for module in iter_import_modules(path)
            if any(
                module == prefix or module.startswith(f"{prefix}.")
                for prefix in forbidden_prefixes
            )
        ]
        if not bad_imports:
            continue
        joined = ", ".join(bad_imports)
        violations.append(f"{path.relative_to(root)} -> {joined}")
    return violations


def _collect_target_names(target: ast.expr) -> set[str]:
    names: set[str] = set()
    if isinstance(target, ast.Name):
        names.add(target.id)
        return names
    if isinstance(target, (ast.Tuple, ast.List)):
        for element in target.elts:
            names.update(_collect_target_names(element))
    return names


def extract_top_level_bindings(path: Path, *, root: Path) -> list[str]:
    """Extract top-level bound names from one module."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    bindings: set[str] = set()
    type_alias = getattr(ast, "TypeAlias", None)

    for node in tree.body:
        if isinstance(node, ast.Import):
            bindings.update(alias.asname or alias.name.split(".")[0] for alias in node.names)
            continue
        if isinstance(node, ast.ImportFrom):
            bindings.update(alias.asname or alias.name for alias in node.names)
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bindings.add(node.name)
            continue
        if isinstance(node, ast.Assign):
            for target in node.targets:
                bindings.update(_collect_target_names(target))
            continue
        if isinstance(node, ast.AnnAssign):
            bindings.update(_collect_target_names(node.target))
            continue
        if type_alias is not None and isinstance(node, type_alias):
            if isinstance(node.name, ast.Name):
                bindings.add(node.name.id)

    if not bindings:
        message = f"Could not find top-level bindings in {path.relative_to(root)}"
        raise AssertionError(message)
    return sorted(bindings)


def extract_all(path: Path, *, root: Path) -> list[str]:
    """Extract `__all__` string exports from one module."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id != "__all__":
            continue
        if not isinstance(node.value, (ast.List, ast.Tuple)):
            continue
        return [
            element.value
            for element in node.value.elts
            if isinstance(element, ast.Constant) and isinstance(element.value, str)
        ]
    message = f"Could not find __all__ in {path.relative_to(root)}"
    raise AssertionError(message)


def extract_property_names(path: Path, class_name: str, *, root: Path) -> set[str]:
    """Extract `@property` names from one class."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        property_names: set[str] = set()
        for child in node.body:
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if any(
                isinstance(decorator, ast.Name) and decorator.id == "property"
                for decorator in child.decorator_list
            ):
                property_names.add(child.name)
        return property_names
    message = f"Could not find class {class_name} in {path.relative_to(root)}"
    raise AssertionError(message)


__all__ = [
    "extract_all",
    "extract_property_names",
    "extract_top_level_bindings",
    "find_forbidden_imports",
    "iter_import_modules",
]
