"""Shared types and row builders for file-matrix registry classification."""

from __future__ import annotations

from dataclasses import dataclass

type ClassifierRule = tuple[str, tuple[str, str, str, str]]


@dataclass(frozen=True, slots=True)
class FileGovernanceRow:
    """One normalized file-governance record from the matrix inventory."""

    path: str
    area: str
    owner_phase: str
    fate: str
    residual: str


@dataclass(frozen=True, slots=True)
class OverrideTruthFamily:
    """One focused override family that contributes file-governance rows."""

    area: str
    owner_phase: str
    rows: tuple[tuple[str, str], ...]
    fate: str = "保留"


@dataclass(frozen=True, slots=True)
class ExactRuleFamily:
    """One family of exact path rules that shares governance metadata."""

    area: str
    owner_phase: str
    fate: str = "保留"
    default_residual: str = "-"
    paths: tuple[str, ...] = ()
    residual_rows: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class PrefixRuleFamily:
    """One family of prefix path rules that shares governance metadata."""

    area: str
    owner_phase: str
    prefixes: tuple[str, ...]
    fate: str = "保留"
    residual: str = "-"


def row_for_path(
    path: str,
    area: str,
    owner_phase: str,
    fate: str = "保留",
    residual: str = "-",
) -> FileGovernanceRow:
    """Build one normalized governance row."""
    return FileGovernanceRow(
        path=path,
        area=area,
        owner_phase=owner_phase,
        fate=fate,
        residual=residual,
    )


def build_exact_rules(*families: ExactRuleFamily) -> tuple[ClassifierRule, ...]:
    """Expand grouped exact-rule families into registry rule tuples."""
    rules: list[ClassifierRule] = []
    for family in families:
        payload = (
            family.area,
            family.owner_phase,
            family.fate,
            family.default_residual,
        )
        rules.extend((path, payload) for path in family.paths)
        rules.extend(
            (path, (family.area, family.owner_phase, family.fate, residual))
            for path, residual in family.residual_rows
        )
    return tuple(rules)


def build_prefix_rules(*families: PrefixRuleFamily) -> tuple[ClassifierRule, ...]:
    """Expand grouped prefix-rule families into registry rule tuples."""
    rules: list[ClassifierRule] = []
    for family in families:
        payload = (family.area, family.owner_phase, family.fate, family.residual)
        rules.extend((prefix, payload) for prefix in family.prefixes)
    return tuple(rules)


__all__ = [
    "ClassifierRule",
    "ExactRuleFamily",
    "FileGovernanceRow",
    "OverrideTruthFamily",
    "PrefixRuleFamily",
    "build_exact_rules",
    "build_prefix_rules",
    "row_for_path",
]
