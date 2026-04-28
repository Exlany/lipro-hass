"""Thin compatibility re-export for architecture policy helpers."""

from __future__ import annotations

from scripts.lib.architecture_policy import (
    ArchitecturePolicyRule,
    load_policy_text,
    load_structural_rules,
    load_targeted_bans,
    policy_path,
    policy_root,
    resolve_policy_paths,
)

__all__ = [
    "ArchitecturePolicyRule",
    "load_policy_text",
    "load_structural_rules",
    "load_targeted_bans",
    "policy_path",
    "policy_root",
    "resolve_policy_paths",
]
