"""Shared structural helpers for dependency guard suites."""
from __future__ import annotations

from pathlib import Path

from tests.helpers.architecture_policy import (
    load_structural_rules,
    policy_root,
    resolve_policy_paths,
)
from tests.helpers.ast_guard_utils import find_forbidden_imports

_ROOT = policy_root(Path(__file__))
_DEPENDENCY_MATRIX = _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
_RULES = load_structural_rules(_ROOT)

def _violations_for_rule(rule_id: str) -> list[str]:
    rule = _RULES[rule_id]
    governed_paths, missing_governed = resolve_policy_paths(
        rule.governed_targets, root=_ROOT
    )
    allowed_paths, missing_allowed = resolve_policy_paths(
        rule.allowed_or_required_signals,
        root=_ROOT,
    )

    missing = [
        *[
            f"{rule_id} unresolved governed path pattern: {pattern}"
            for pattern in missing_governed
        ],
        *[
            f"{rule_id} unresolved allowed path pattern: {pattern}"
            for pattern in missing_allowed
        ],
    ]
    if missing:
        return missing

    allowed_path_set = set(allowed_paths)
    scanned_paths = [path for path in governed_paths if path not in allowed_path_set]
    violations = find_forbidden_imports(
        scanned_paths,
        tuple(rule.forbidden_signals),
        root=_ROOT,
    )
    return [f"{rule_id}: {violation}" for violation in violations]

__all__ = ["_DEPENDENCY_MATRIX", "_ROOT", "_violations_for_rule"]
